import datetime
from functools import lru_cache
from jwcrypto import jwt

from services.licensing import settings


@lru_cache(maxsize=64)
def get_key_from_pem(key_pem: str | bytes) -> jwt.JWK:
    """
    (creates and) gets a key (private or public) from a given PEM (PKCS#8)
    structure. As sometimes this operation is expensive, we use some cache here!
    This function basically wraps the jwt.JWK.from_pem function and additionally
    using a cache.
    :param key_pem: the private key to use as PEM formatted string
    :return: the key as a jwt.JWK structure
    """
    # some hack to provide correct format in case of key provided as string ...
    if isinstance(key_pem, str):
        key_pem = key_pem.encode("utf-8").replace(b"\\n", b"\n")
    return jwt.JWK.from_pem(key_pem)


def get_expiration_timestamp(offset_secs: int) -> float:
    """gets a timestamp for a given time offset in secs from now."""
    return (
        datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=offset_secs)
    ).timestamp()


def create_licensing_token(claims: dict):
    """
    creates a JWT token based on EC-256 algorithm using the
    'licensing service' private key.
    :param claims: the claims as a dict
    :return:
    """
    token = jwt.JWT(
        header={"typ": "JWT", "kid": settings.licensing_service_kid, "alg": "ES256"},
        claims=claims,
    )
    token.make_signed_token(get_key_from_pem(settings.licensing_service_private_key))
    return token.serialize()


def create_shop_token(claims: dict):
    """
    Creates a JWT token based on EC-256 algorithm using the 'shop service' private key.
    todo: should be moved to `shop` service
    :param claims: the claims as a dict
    :return:
    """
    token = jwt.JWT(
        header={"typ": "JWT", "kid": settings.shop_service_kid, "alg": "ES256"},
        claims=claims,
    )
    token.make_signed_token(get_key_from_pem(settings.shop_service_private_key))
    return token.serialize()
