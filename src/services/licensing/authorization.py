import hashlib
import json
from functools import partial
from typing import Any, Dict, List, Optional, Tuple
from fastapi import Depends, Request
from fastapi import status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from jwcrypto import jwt, jws

from services.licensing.exceptions import HTTPException
from services.licensing import settings
from services.licensing.tokens import get_key_from_pem

# a 401 HTTP Exception shortcut used below ...
HTTP401 = partial(HTTPException, status_code=http_status.HTTP_401_UNAUTHORIZED)

# supported hash algorithms for payload hashes encoded into JWT tokens ...
HASHING_ALGORITHMS = {"SHA256": hashlib.sha256}


class CustomHTTPBearer(HTTPBearer):
    """
    slightly modified HTTPBearer class. Reads the authorization header,
    perform some initial checks and returns the resulting JWT token.
    """

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)

        if not authorization or not scheme or not credentials:
            raise HTTP401(message="Invalid or missing authorization header")
        if scheme.lower() != "bearer":
            raise HTTP401(message="Invalid authorization scheme")
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class PayloadForHashing:
    """
    reads the request body and extracts some requested parameter
    used to check a given hash for
    """

    def __init__(self, payload_key: str):
        self.payload_key = payload_key

    async def __call__(self, request: Request) -> str:
        return (await request.json()).get(self.payload_key)


def check_hash(payload_key, payload, payload_hash_dict):
    """
    helper: checks for matching hashes. Given a 'payload_key', something
    like 'memberships', a payload, that represents the data structure to hash
    (some 'memberships' object) and some data structure representing the hash
    algorithm and the hash of the datastructure itself as it is encoded in
    the given JWT token (something like
       "memberships": {
           "alg": "SHA256",
           "hash": "06a92309619f40334e3ad2f5c8b80984b0d642e1fb48dc85a0..."
       }
    ), this function builds the hash using some hash algorithm (usually SHA256)
    over the given data structure (e.g. 'memberships' object) and compares to the
    also provided hash given in the 'payload_hash_dict' structure.

    :param payload_key: some string representing the payload structure to hash
    :param payload: some object to hash
    :param payload_hash_dict: structure holding the hash to be compared to.
    :returns: None in case of success
    :raises: an HTTP 401 error in case of failing hash comparison or missing data
    """
    hash_dict = payload_hash_dict.get(payload_key)
    if not hash_dict:
        raise HTTP401(
            message="Token does not contain requested payload hash",
            payload_key=payload_key,
        )
    if payload is None:
        raise HTTP401(message="No payload available to compare with payload hash")
    hashing_alg = HASHING_ALGORITHMS.get(hash_dict.get("alg", "undefined").upper())
    if not hashing_alg:
        raise HTTP401(
            message="Unsupported hash algorithm", hash_algorithm=hash_dict.get("alg")
        )

    h0 = hashing_alg(json.dumps(payload).encode("utf-8")).hexdigest()
    h1 = hash_dict.get("hash")
    if h0 != h1:
        raise HTTP401(
            message="Payload hash does not match signed hash, maybe has been tampered",
            payload_hash=h0,
            signed_hash=h1,
        )


def get_key(kid):
    """
    gets a JWK formatted key from a given KID. Currently only PEM
    formatted keys are supported, no passphrase or other keys.
    :param kid: the given keyID (kid)
    :returns: a valid key (JWK object) gotten from the keyID
    :raises: a 401, if the kid could not be identified
    """
    try:
        return get_key_from_pem(
            settings.jwt_verification_keys[kid]["key"].encode("utf-8")
        )
    except KeyError:
        raise HTTP401(message="Key ID (kid) cannot be identified", kid=kid)


async def authorize(
    credentials: HTTPAuthorizationCredentials, requested_claim_keys: List[str] | None
) -> Tuple[str, Dict]:
    """
    checks validity of a token and returns the payload, if valid.
    :param credentials: injected HTTPAuthorizationCredentials object from auth header
    :param requested_claim_keys: a list of 'claim keys' that are required.
    :return: (the token, a dict got from the 'requested' claims keys).
    """
    try:
        # deserialize nested token without decryption to get kid ...
        jws_token = jwt.JWS()
        jws_token.deserialize(credentials.credentials)
        jws_kid = jws_token.jose_header["kid"]

        # verify ...
        jwt_token = jwt.JWT(key=get_key(jws_kid), jwt=credentials.credentials)
        claims = json.loads(jwt_token.claims)

    except (jwt.JWTExpired, jwt.JWTInvalidClaimValue, KeyError) as exc:
        raise HTTP401(message="JWT token validation failed", exception=str(exc))
    except jws.InvalidJWSSignature as exc:
        raise HTTP401(
            message="JWS token signature validation failed", exception=str(exc)
        )

    # get the claims
    try:
        requested_claims = {
            claim_key: claims[claim_key] for claim_key in (requested_claim_keys or ())
        }
    except KeyError as exc:
        raise HTTP401(
            message="Token does not contain requested claim",
            requested_claim_key=exc.args[0],
        )
    else:
        return credentials.credentials, requested_claims


async def authorize_with_token(
    credentials: HTTPAuthorizationCredentials = Depends(CustomHTTPBearer()),
) -> Tuple[str, Dict]:
    """
    checks the authorization header to be a valid token, but without any payload
    :param credentials: injected HTTPAuthorizationCredentials object from auth header
    :return: (the issuer URL, the subject (user EID), None)
    :raises: 401 in case of unsuccessful token validation
    """
    return await authorize(credentials, None)


async def authorize_with_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(CustomHTTPBearer()),
) -> Tuple[str, Dict[str, Any]]:
    """
    checks the authorization header to be a valid 'admin token'
    :param credentials: injected HTTPAuthorizationCredentials object from auth header
    :return: (the token itself, a requested subset of the payload dict)
    :raises: 401 in case of unsuccessful token validation
    """
    return await authorize(credentials, ["filter_restrictions"])


async def authorize_with_memberships_token(
    credentials: HTTPAuthorizationCredentials = Depends(CustomHTTPBearer()),
    memberships: Any = Depends(PayloadForHashing("memberships")),
) -> Tuple[str, Dict[str, Any]]:
    """
    checks the authorization header to be a valid 'membership token'
    :param credentials: injected HTTPAuthorizationCredentials object from auth header
    :param memberships: injected requested value for a given key from the request body
    :return: (the token itself, a requested subset of the payload dict)
    :raises: 401 in case of unsuccessful token validation
    """
    token, payload = await authorize(credentials, ["iss", "sub", "hashes"])
    check_hash("memberships", memberships, payload["hashes"])
    return token, payload


async def authorize_with_hierarchies_token(
    credentials: HTTPAuthorizationCredentials = Depends(CustomHTTPBearer()),
    hierarchies: Any = Depends(PayloadForHashing("hierarchies")),
) -> Tuple[str, Dict[str, Any]]:
    """
    checks the authorization header to be a valid 'hierarchies token'
    :param credentials: injected HTTPAuthorizationCredentials object from auth header
    :param hierarchies: injected requested value for a given key from the request body
    :return: (the token itself, a requested subset of the payload dict)
    :raises: 401 in case of unsuccessful token validation
    """
    token, payload = await authorize(credentials, ["iss", "sub", "hashes"])
    check_hash("hierarchies", hierarchies, payload["hashes"])
    return token, payload


async def authorize_with_shop_token(
    credentials: HTTPAuthorizationCredentials = Depends(CustomHTTPBearer()),
) -> Tuple[str, Dict]:
    """
    checks the authorization header to be a valid 'shop token'
    :param credentials: injected HTTPAuthorizationCredentials object from auth header
    :return: (the issuer URL, the subject (user EID), the ordering payload structure)
    :raises: 401 in case of unsuccessful token validation
    """
    return await authorize(credentials, ["sub", "order"])
