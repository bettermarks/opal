import functools
import re
from typing import Any, Annotated, Union

from fastapi import APIRouter, Header, Response
from fastapi.openapi.utils import get_openapi
from jsonschema import validate, ValidationError


def primitive_type_example(schema_type: str, schema_format: str | None = None) -> Any:
    """Defaults for primitive types."""
    match schema_type:
        case "string":
            match schema_format:
                case "uuid":
                    example = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                case "date":
                    example = "2023-12-31"
                case "date-time":
                    example = "2023-12-31 23:59:59"
                case "email":
                    example = "user@example.com"
                case "hostname":
                    example = "example.com"
                case "ipv4":
                    example = "127.0.0.1"
                case "ipv6":
                    example = "0000:0000:0000:0000:0000:0000:0000:0000"
                case _:
                    example = "string"
        case "integer":
            example = 0
        case "number":
            if schema_format == "float":
                example = 0
            else:
                example = 0
        case "boolean":
            example = True
        case "object":
            example = {}
        case _:
            example = None
    return example


def recursive_schema_parse(
    schema_name: str, schema_dict: dict, schemas_map: dict, parsed_schemas: dict
) -> tuple[str, Any]:
    """
    Recursively parse OpenAPI schema.
    :param schema_name: (str) name of a schema being parsed by calling this function
    :param schema_dict: (dict) content of schema being parsed by calling this function
    :param schemas_map: (dict) contains all schemas from an openapi specification
    :param parsed_schemas: (set) contains names of all schemas parsed by recursive
    parser and used to avoid circular references
    """
    schema_format = schema_dict.get("format")
    # extract first type in `anyOf` in `type` field
    if any_of := schema_dict.pop("anyOf", {}):
        if not (len(any_of) == 2 and any_of[1]["type"] == "null"):
            raise ValueError(f"unexpected anyOf in schema: {any_of}")
        schema_dict["type"] = any_of[0]["type"]
    match schema_type := schema_dict.get("type"):
        case "object":
            example = {}
            if props := schema_dict.get("properties"):
                for prop_name, prop_dict in props.items():
                    # (!!!) recursion enter
                    result_prop_name, result_example = recursive_schema_parse(
                        prop_name, prop_dict, schemas_map, parsed_schemas
                    )
                    example[result_prop_name] = result_example
        case "array":
            if items := schema_dict.get("items"):
                if item_ref := items.get("$ref"):
                    # (!!!) sub-recursion to process reference
                    sub_schema_name = item_ref.split("/")[-1]
                    if sub_schema_name in parsed_schemas:
                        # this approach is used in `fastapi` to solve infinite recursion
                        # for self-related schemas
                        sub_example = parsed_schemas[sub_schema_name]
                    else:
                        parsed_schemas[sub_schema_name] = "string"
                        sub_schema_dict = schemas_map[sub_schema_name]
                        _, sub_example = recursive_schema_parse(
                            sub_schema_name,
                            sub_schema_dict,
                            schemas_map,
                            parsed_schemas,
                        )
                        parsed_schemas[sub_schema_name] = sub_example
                    example = [sub_example]
                elif item_type := items.get("type"):
                    example = item_type
                else:
                    example = []
            elif items is None:
                raise ValueError("unprocessed array due to lack of `items` property")
            else:
                example = []
        case "string":
            example = primitive_type_example(schema_type, schema_format)
        case "boolean":
            example = primitive_type_example(schema_type, schema_format)
        case "integer":
            example = primitive_type_example(schema_type, schema_format)
        case "number":
            example = primitive_type_example(schema_type, schema_format)
        case _:
            if "enum" in schema_dict:
                example = schema_dict["enum"][0]
            elif "$ref" in schema_dict:
                item_ref = schema_dict["$ref"]
                # (!!!) sub-recursion to process reference
                sub_schema_name = item_ref.split("/")[-1]
                if sub_schema_name in parsed_schemas:
                    # this approach is used in `fastapi` to solve infinite recursion
                    # for self-related schemas
                    sub_example = parsed_schemas[sub_schema_name]
                else:
                    parsed_schemas[sub_schema_name] = "string"
                    sub_schema_dict = schemas_map[sub_schema_name]
                    _, sub_example = recursive_schema_parse(
                        sub_schema_name, sub_schema_dict, schemas_map, parsed_schemas
                    )
                    parsed_schemas[sub_schema_name] = sub_example
                example = sub_example
            else:
                raise ValueError(f"unprocessed type [{schema_type}]")
    return schema_name, example


def build_regex_paths_map(
    openapi_spec: dict, regex_placeholder: str = "[a-zA-Z0-9-_]+"
) -> dict[str, dict]:
    """
    Builds a mapping of paths (from `openapi_spec.paths`) to response
    specifications. Paths are converted into regexps, suitable for `re.match`, then
    they are used as keys of result dictionary, values are those path response
    specifications.
    Example of path conversion: /v1/some/path/{value} -> ^/v1/some/path/[a-z-A-Z0-9-_]$
    """
    regex_paths_map = {}
    for schema_route, spec in openapi_spec.get("paths", dict()).items():
        key_route = f"^{schema_route}$"
        for param in re.findall(r"{[a-zA-Z0-9_]+}", schema_route):
            key_route = key_route.replace(param, regex_placeholder)
        # fill mapping with {...key_route: spec...}
        regex_paths_map[key_route] = spec
    return regex_paths_map


def extract_schema_name(response_schema: dict) -> str:
    """
    Extract schema name of `$ref` (i.e. the last_part of a $/schema/path/last_part).
    """
    try:
        if "anyOf" in response_schema:
            schema = response_schema["anyOf"][0]
        else:
            schema = response_schema
        return schema["$ref"].split("/")[-1]
    except KeyError:
        raise ValueError("no $ref in a provided response_schema")


def extract_schema(openapi_spec: dict, response_schema: dict) -> tuple[dict, str, dict]:
    """
    - Extract schema name of `$ref` (i.e. the last_part of a $/schema/path/last_part).
    - Extract schema dictionary from openapi specification component schemas list.
    :returns: Tuple of schemas_map, schema_name, schema_dict
    """
    schema_name = extract_schema_name(response_schema)

    try:
        schemas_map = openapi_spec["components"]["schemas"]
        schema_dict = schemas_map[schema_name]
    except KeyError:
        raise ValueError(
            f"schemas are not defined in openapi spec or "
            f"schema `{schema_name}` is not presented there"
        )
    return schemas_map, schema_name, schema_dict


def validate_request_body(
    openapi_spec: dict,
    request_method: str,
    request_body: dict | None,
    preferred_spec: dict,
):
    """..."""
    if request_method in {"post", "put", "patch"} and request_body:
        if body_schema := preferred_spec[request_method].get("requestBody"):
            response_content_json = body_schema["content"]["application/json"]
            if response_schema := response_content_json.get("schema"):
                _, _, schema_dict = extract_schema(openapi_spec, response_schema)
                try:
                    validate(request_body, schema_dict)
                except ValidationError:
                    raise ValueError(
                        "provided request body is not matching an openapi specification"
                    )
        else:
            raise ValueError("request body is not expected in this request")


async def example_openapi_response(
    openapi_spec: dict,
    request_path: str,
    request_method: str,
    request_body: dict | None,
    response_status: int | str,
    response_example: str | None = None,
) -> tuple[int, dict]:
    """
    Function returns an example response from the given `openapi_spec`, based on
    `request_path`, `request_method` and desired `response_status`.

    :param openapi_spec: (dict) open api specification
    :param request_path: (str) request path to search in a specification
    :param request_method: (str) request method to search in a specification
    :param request_body: (dict) request body to check for validity
    :param response_status: (optional int) desired response status
    :param response_example: (optional string) extract name example from `examples` key
    """
    request_method = request_method.lower()
    response_status = str(response_status)

    # generate {..., "re_path" -> path_spec{}, ...}
    regex_paths_map = build_regex_paths_map(openapi_spec)

    # selecting preferred response
    preferred_spec = None
    for regex, spec in regex_paths_map.items():
        if re.match(regex, request_path):
            preferred_spec = spec
            break

    # early exit conditions (i.e. validation)
    if not regex_paths_map:
        raise ValueError("openapi specification was not parsed")
    elif not preferred_spec:
        raise ValueError(f"path [{request_path}] is not in openapi specification")
    elif request_method not in preferred_spec:
        raise ValueError("method is not in response specification")

    # validating inbound request `body`
    validate_request_body(openapi_spec, request_method, request_body, preferred_spec)

    # search for response schema `$ref`
    responses = preferred_spec[request_method]["responses"]
    if response_status not in responses:
        raise ValueError("response status is not in path responses")

    # extract response example if it was requested explicitly
    response_content_json = responses[response_status]["content"]["application/json"]
    if response_example:
        examples = response_content_json.get("examples", {})
        if response_example in examples:
            example = examples[response_example]["value"]
        else:
            raise ValueError(f"response example `{response_example}` is not defined")
    else:
        # get schema `$ref`, extract schema name and get an example for that schema
        if response_schema := response_content_json.get("schema"):
            schemas_map, schema_name, schema_dict = extract_schema(
                openapi_spec, response_schema
            )
            _, example = recursive_schema_parse(
                schema_name, schema_dict, schemas_map, dict()
            )
        else:
            example = primitive_type_example("string")

    return int(response_status), example


@functools.cache
def get_openapi_schema(
    title: str = "Generated Pacts API", version: str = "1.0.0"
) -> dict:
    """Get OpenAPI v3 schema from FastAPI service router."""
    from services.licensing.main import api_router

    return get_openapi(title=title, version=version, routes=api_router.routes)


async def pact_responder(
    scope_method: str,
    orig_path: str,
    body: dict | None = None,
    desired_status: int | None = None,
    desired_example: str | None = None,
) -> tuple[int, dict]:
    """
    Generic responder function. Invariant for pact endpoints.

    :param scope_method: (str) 'GET', 'POST', 'PUT'
    :param orig_path: (str) request path from method responders
    :param body: (optional dict) request body for a request
    :param desired_status: (optional int) desired response `status code`,
    controls which response is to generate
    :param desired_example: (optional str) desired response `example`,
    controls which response is to generate. Use in a case when openapi specification
    defines named example responses.
    """
    openapi_schema = get_openapi_schema()
    if not orig_path.startswith("/"):
        orig_path = f"/{orig_path}"
    request_body = {} if body is None else body
    return await example_openapi_response(
        openapi_schema,
        orig_path,
        scope_method,
        request_body,
        response_status=desired_status,
        response_example=desired_example,
    )


# FastAPI router with generic pact endpoints
pact_router = APIRouter()


@pact_router.get("/{orig_path:path}", response_model=None)
async def pacts_get(
    orig_path: str,
    response: Response,
    x_pact_desired_status: Annotated[Union[int, None], Header()] = 200,
    x_pact_desired_example: Annotated[Union[str, None], Header()] = None,
):
    """Responder endpoint for `GET` method."""
    status_code, response_data = await pact_responder(
        "get",
        orig_path,
        desired_status=x_pact_desired_status,
        desired_example=x_pact_desired_example,
    )
    response.status_code = status_code
    return response_data


@pact_router.post("/{orig_path:path}", response_model=None)
async def pacts_post(
    orig_path: str,
    body: dict,
    response: Response,
    x_pact_desired_status: Annotated[Union[int, None], Header()] = 201,
    x_pact_desired_example: Annotated[Union[str, None], Header()] = None,
):
    """Responder endpoint for `POST` method."""
    status_code, response_data = await pact_responder(
        "post",
        orig_path,
        body,
        desired_status=x_pact_desired_status,
        desired_example=x_pact_desired_example,
    )
    response.status_code = status_code
    return response_data


@pact_router.put("/{orig_path:path}", response_model=None)
async def pacts_put(
    orig_path: str,
    body: dict,
    response: Response,
    x_pact_desired_status: Annotated[Union[int, None], Header()] = 200,
    x_pact_desired_example: Annotated[Union[str, None], Header()] = None,
):
    """Responder endpoint for `PUT` method."""
    status_code, response_data = await pact_responder(
        "put",
        orig_path,
        body,
        desired_status=x_pact_desired_status,
        desired_example=x_pact_desired_example,
    )
    response.status_code = status_code
    return response_data


@pact_router.delete("/{orig_path:path}", response_model=None)
async def pacts_delete(
    orig_path: str,
    response: Response,
    x_pact_desired_status: Annotated[Union[int, None], Header()] = 200,
    x_pact_desired_example: Annotated[Union[str, None], Header()] = None,
):
    """Responder endpoint for `DELETE` method."""
    status_code, response_data = await pact_responder(
        "delete",
        orig_path,
        desired_status=x_pact_desired_status,
        desired_example=x_pact_desired_example,
    )
    response.status_code = status_code
    return response_data
