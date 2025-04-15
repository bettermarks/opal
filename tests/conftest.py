from typing import Dict

import pytest

from jwcrypto import jwt, jwk

SHOP_SERVICE_KID = "SHOP_SERVICE_KID"
HIERARCHY_PROVIDER_KID = "HIERARCHY_PROVIDER_KID"
BACKOFFICE_KID = "BACKOFFICE_KID"
NOT_EXISTING_KID = "NOT_EXISTING_KID"
INVALID_SIGNATURE_KEY_KID = "INVALID_SIGNATURE_KEY_KID"
LICENSING_SERVICE_KID = "LICENSING_KID"

# we use 256 bit elliptic curve keys
TEST_HP_EC256_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgJ4/5yLFU96V7miX2
G1mgKLB3t9p8JdVbm89BezDKdA6hRANCAASY+6sGCs5Vua6NCw/2gdLkT8v5ttIA
m0f74KpTo2UL/zCpH9L3Gq/gOmSjs0MCkX4avWRpH6iUdCd56IdEgK46
-----END PRIVATE KEY-----
"""

TEST_HP_EC256_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEmPurBgrOVbmujQsP9oHS5E/L+bbS
AJtH++CqU6NlC/8wqR/S9xqv4Dpko7NDApF+Gr1kaR+olHQneeiHRICuOg==
-----END PUBLIC KEY-----
"""

TEST_SS_EC256_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgNncIejvJwudHuhVS
RmrQfnhURO26FXMXOdLP63bai5+hRANCAAQ6MDqb+wffBQd/vSEBvFMrUe4BTA0u
uu5RU6UzBYhiV4RlIZAbN0LklD16BFn5EKe1dpRmvKh4ivN/hsHwN/Tv
-----END PRIVATE KEY-----
"""

TEST_SS_EC256_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOjA6m/sH3wUHf70hAbxTK1HuAUwN
LrruUVOlMwWIYleEZSGQGzdC5JQ9egRZ+RCntXaUZryoeIrzf4bB8Df07w==
-----END PUBLIC KEY-----
"""

TEST_BO_EC256_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg0VKjq/HU+MiX1wu6
BeLUmqmAQECrncf6D+ywzSf9Bw6hRANCAASBFziT/yaDI7+Z2/pRJyT53dObRTSS
Z+fsvuZrO6XxTW8KozlxdU49xjhCeH9sZz4xlrkJgCre29fTiS/eeUin
-----END PRIVATE KEY-----
"""

TEST_BO_EC256_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEgRc4k/8mgyO/mdv6USck+d3Tm0U0
kmfn7L7mazul8U1vCqM5cXVOPcY4Qnh/bGc+MZa5CYAq3tvX04kv3nlIpw==
-----END PUBLIC KEY-----
"""

TEST_INVALID_SIGNATURE_EC256_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgJ4/5yLFU96V7miX2
G1mgKLB3t9p8JdVbm89BezDKdA6hRANCAASY+6sGCs5Vua6NCw/2gdLkT8v5ttIA
m0f74KpTo2UL/zCpH9L3Gq/gOmSjs0MCkX4avWRpH6iUdCd56IdEgK46
-----END PRIVATE KEY-----
"""

TEST_INVALID_SIGNATURE_EC256_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE281l1rMrVK+3RCst93avfl6JWFc/
AYWlisHco7a3c+3Ob1OJQLhmDqEBszJpc6wsYsfaVW7USxsyEz0A/lQXpg==
-----END PUBLIC KEY-----
"""

TEST_LICENSING_SERVICE_EC256_PRIVATE_KEY = """
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgRLrl+FraA4fDhod9
RsD6azYgqdcCZwgqQcEWG8AC4FChRANCAAQEj80O7Hs8/woLEfHCTafEYoMFQzYa
JVrHQG+d17TIuxEhL+MjBne3ovJl8/vPNlsyKPUYgtaYLpVlpBu5ovPe
-----END PRIVATE KEY-----
"""

TEST_LICENSING_SERVICE_EC256_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBI/NDux7PP8KCxHxwk2nxGKDBUM2
GiVax0Bvnde0yLsRIS/jIwZ3t6LyZfP7zzZbMij1GILWmC6VZaQbuaLz3g==
-----END PUBLIC KEY-----
"""

TEST_LICENSING_SERVICE_URL = "http://test-licesning-service-url.com"


# various settings mock
@pytest.fixture(autouse=True)
def test_settings(mocker):
    mocker.patch(
        "services.licensing.settings.licensing_service_url", TEST_LICENSING_SERVICE_URL
    )


# kid lookup mock!
@pytest.fixture(autouse=True)
def test_jwt_keys(mocker):
    mocker.patch(
        "services.licensing.settings.jwt_verification_keys",
        {
            HIERARCHY_PROVIDER_KID: {
                "format": "pem",
                "desc": "used as public (EC) JWS signature key OF hierarchy provider",
                "key": TEST_HP_EC256_PUBLIC_KEY,
            },
            SHOP_SERVICE_KID: {
                "format": "pem",
                "desc": "used as public (EC) JWS signature key OF shop service",
                "key": TEST_SS_EC256_PUBLIC_KEY,
            },
            BACKOFFICE_KID: {
                "format": "pem",
                "desc": "used as public (EC) JWS signature key OF backoffice service",
                "key": TEST_BO_EC256_PUBLIC_KEY,
            },
            INVALID_SIGNATURE_KEY_KID: {
                "format": "pem",
                "desc": "used as public (EC) JWS signature key OF some other service",
                "key": TEST_INVALID_SIGNATURE_EC256_PUBLIC_KEY,
            },
        },
    )
    mocker.patch(
        "services.licensing.settings.licensing_service_kid",
        "ff0c1ec8-42e3-4312-b35e-5a7c795eddd4",
    )
    mocker.patch(
        "services.licensing.settings.licensing_service_private_key",
        TEST_LICENSING_SERVICE_EC256_PRIVATE_KEY,
    )


def get_private_key(kid: str):
    if kid == HIERARCHY_PROVIDER_KID:
        return jwk.JWK.from_pem(TEST_HP_EC256_PRIVATE_KEY.encode("utf-8"))
    if kid == SHOP_SERVICE_KID:
        return jwk.JWK.from_pem(TEST_SS_EC256_PRIVATE_KEY.encode("utf-8"))
    if kid == BACKOFFICE_KID:
        return jwk.JWK.from_pem(TEST_BO_EC256_PRIVATE_KEY.encode("utf-8"))
    if kid == NOT_EXISTING_KID:
        return jwk.JWK.from_pem(TEST_BO_EC256_PRIVATE_KEY.encode("utf-8"))
    if kid == INVALID_SIGNATURE_KEY_KID:
        return jwk.JWK.from_pem(
            TEST_INVALID_SIGNATURE_EC256_PRIVATE_KEY.encode("utf-8")
        )
    raise ValueError("Unknown KID")


def create_token(private_kid, iss, exp, sub, payload: Dict = None):
    token = jwt.JWT(
        header={"typ": "JWT", "alg": "ES256", "kid": private_kid},
        claims={"iss": iss, "exp": exp, "sub": sub} | (payload if payload else {}),
    )
    token.make_signed_token(get_private_key(private_kid))
    return token.serialize()
