# TODO -> As we do not use Licensing service as a client currently -> module DEPRECATED

import httpx

from services.licensing.exceptions import HTTPException


async def get_request(url: str, authorization_token: str = None):
    """
    calls a given URL with a GET request using some optional
    authorization token and returns the response OR raises an
    HTTPException
    :param url: the url to call (back)
    :param authorization_token: the token to be used (optional)
    :return: the response returned
    :raises: a HTTPException (500) on failure.
    """
    headers = {"Authorization": f"Bearer {authorization_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, message=response.text)


async def post_request(
    url: str,
    data: dict = None,
    json: dict = None,
    authorization_token: str = None,
    authorization_api_key: str = None,
    authorization_basic: tuple[str, str] = None,
):
    """
    calls a given URL with a POST request using some optional
    authorization token and returns the response OR raises an
    HTTPException
    :param url: the url to call (back)
    :param data: request form data parameter (optional)
    :param json: request json data parameter (optional)
    :param authorization_token: the token to be used (optional)
    :param authorization_api_key: an optional API key
    :param authorization_basic: login/password pair to be used (optional)
    :return: the response returned
    :raises: a HTTPException on failure.
    """
    params = {}
    if authorization_token:
        params.update({"headers": {"Authorization": f"Bearer {authorization_token}"}})
    if authorization_api_key:
        params.update({"headers": {"x-api-key": authorization_api_key}})
    if authorization_basic:
        params.update({"auth": authorization_basic})
    if data is not None:
        params.update({"data": data})
    elif json is not None:
        params.update({"json": json})
    async with httpx.AsyncClient() as client:
        response = (
            await client.post(url, **params)
            if ("data" in params or "json" in params)
            else await client.get(url, **params)
        )
        if 200 <= response.status_code <= 202:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, message=response.text)
