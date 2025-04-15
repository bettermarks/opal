import pytest

from services.licensing.pacts import (
    build_regex_paths_map,
    extract_schema,
    extract_schema_name,
    example_openapi_response,
    validate_request_body,
)


@pytest.fixture()
def openapi_schema():
    return {
        "openapi": "3.1.0",
        "info": {"title": "Licensing API", "version": "1.0.0"},
        "paths": {
            "/admin/licenses": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "Get Licenses",
                    "description": 'The "get licenses" route for admins\n:param product_eid\n:param owner_type\n:param owner_level\n:param owner_eid\n:param manager_eid\n:param valid_from\n:param valid_to\n:param is_trial\n:param is_valid\n:param created_at\n:param redeemed_seats: \'percentage of occupied seats - filter\n:param order_by something like "-id.valid_from.-manager_eid.-product_eid\n:param token_data\n:return: a JSON object (usually a list of licenses)',
                    "operationId": "get_licenses_admin_licenses_get",
                    "parameters": [
                        {
                            "required": False,
                            "schema": {"type": "string", "title": "Product Eid"},
                            "name": "product_eid",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "string", "title": "Owner Type"},
                            "name": "owner_type",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "integer", "title": "Owner Level"},
                            "name": "owner_level",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "string", "title": "Owner Eid"},
                            "name": "owner_eid",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "string", "title": "Manager Eid"},
                            "name": "manager_eid",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {
                                "type": "string",
                                "format": "date",
                                "title": "Valid From",
                            },
                            "name": "valid_from",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {
                                "type": "string",
                                "format": "date",
                                "title": "Valid To",
                            },
                            "name": "valid_to",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "boolean", "title": "Is Trial"},
                            "name": "is_trial",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "boolean", "title": "Is Valid"},
                            "name": "is_valid",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {
                                "type": "string",
                                "format": "date",
                                "title": "Created At",
                            },
                            "name": "created_at",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "integer", "title": "Redeemed Seats"},
                            "name": "redeemed_seats",
                            "in": "query",
                        },
                        {
                            "required": False,
                            "schema": {"type": "string", "title": "Order By"},
                            "name": "order_by",
                            "in": "query",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CustomizedPage_LicenseCompleteSchema_"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                },
                "post": {
                    "tags": ["Admin"],
                    "summary": "Create License",
                    "description": "The 'create a license' route for use in administrative procedures.\n:param data: entity attributes dictionary for a license creation\n:param _: info gotten from ordering token (not used, but necessary)\n:returns: some params of the created license or some error\n          message in case of an error",
                    "operationId": "create_license_admin_licenses_post",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LicenseCreateSchema"
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "201": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LicenseCreatedSchema"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                },
            },
            "/admin/licenses/{license_uuid}": {
                "get": {
                    "tags": ["Admin"],
                    "summary": "Get License",
                    "description": 'The "get details for a specific license" route for admins\n:param license_uuid: the `uuid` of the `License` entity to be selected as the result\n:param token_data: data gotten from admin token\n:return: a JSON object representing the license details',
                    "operationId": "get_license_admin_licenses__license_uuid__get",
                    "parameters": [
                        {
                            "required": True,
                            "schema": {"type": "string", "title": "License Uuid"},
                            "name": "license_uuid",
                            "in": "path",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LicenseCompleteSchema"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                },
                "put": {
                    "tags": ["Admin"],
                    "summary": "Update License",
                    "description": "The update license route for admins.\n:param license_uuid: the `uuid` of the license to modify\n:param license_update: the data to update the license with\n:param token_data: data gotten from admin token",
                    "operationId": "update_license_admin_licenses__license_uuid__put",
                    "parameters": [
                        {
                            "required": True,
                            "schema": {"type": "string", "title": "License Uuid"},
                            "name": "license_uuid",
                            "in": "path",
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LicenseUpdateSchema"
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {"application/json": {"schema": {}}},
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                },
                "delete": {
                    "tags": ["Admin"],
                    "summary": "Delete License",
                    "operationId": "delete_license_admin_licenses__license_uuid__delete",
                    "parameters": [
                        {
                            "required": True,
                            "schema": {"type": "string", "title": "License Uuid"},
                            "name": "license_uuid",
                            "in": "path",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {"application/json": {"schema": {}}},
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                },
            },
            "/status": {
                "get": {
                    "tags": ["Status"],
                    "summary": "Get Status",
                    "operationId": "get_status_status_get",
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "title": "Response Get Status Status Get",
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/member/permissions": {
                "post": {
                    "tags": ["Member"],
                    "summary": "Get Accessible Products",
                    "description": 'The "permission" route for a given user\n:param data: a membership data structure used to get the permissions for\n:param token_data: info gotten from memberships token\n:return: a JSON object (usually a list of accessible product EIDs)',
                    "operationId": "get_accessible_products_member_permissions_post",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/MembershipsSchema"
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "string",
                                        "title": "Response Get Accessible Products Member Permissions Post",
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
            "/member/licenses/trial": {
                "post": {
                    "tags": ["Member"],
                    "summary": "Create Trial License",
                    "description": "The 'create a trial license route\n:param data: payload\n:param token_data: info gotten from memberships token\n:returns: some params of the created license or some error\n          message in case of an error",
                    "operationId": "create_trial_license_member_licenses_trial_post",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LicenseTrialSchema"
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "201": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LicenseCreatedSchema"
                                    }
                                }
                            },
                        },
                        "409": {
                            "description": "Duplicate Error",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "detail": "Trial license creation failed: A trial license for this entity already exists"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
            "/member/licenses": {
                "post": {
                    "tags": ["Member"],
                    "summary": "Get Available Licenses",
                    "description": 'Route for getting all licenses that are available in the entities a given user is\nmember of.\n\n### Example Bearer Token structure\n```\n{\n    "iss": "https://acc.bettermarks.com/ucm",\n    "exp": 1701799583.393268,\n    "sub": "3@DE_bettermarks",\n    "iat": 1701798983.393283,\n    "jti": "77ab5b01-83a0-44f3-a086-d25162aae84e",\n    "hashes": {\n        "memberships": {\n        "alg": "SHA256",\n        "hash": "4c8c51dd16136b9905908bc3b6b938067e002e4345679c950abf86a3e2ce05ce"\n        }\n    }\n    }\n```',
                    "operationId": "get_available_licenses_member_licenses_post",
                    "parameters": [
                        {
                            "required": False,
                            "schema": {"type": "string", "title": "Order By"},
                            "name": "order_by",
                            "in": "query",
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/MembershipsSchema"
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CustomizedPage_LicenseAvailableSchema_"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
            "/hierarchy/licenses": {
                "post": {
                    "tags": ["Hierarchy"],
                    "summary": "Get Managed Licenses",
                    "description": 'All licenses in the hierarchy of a given user that they are managing / have created.\n\n### Example Bearer Token structure\n```\n{\n    "iss": "https://acc.bettermarks.com/ucm",\n    "exp": 1701789570.99798,\n    "sub": "12@EN_test",\n    "iat": 1701788970.99799,\n    "jti": "2b47ca46-28b9-4b8d-bd1c-a893acb9de29",\n    "hashes": {\n        "memberships": {\n            "alg": "SHA256",\n            "hash": "86f8b8313c183b3f9ee74b9c042ee440b894f690e9f6308de3da63fd4a6b8"\n        }\n    }\n}\n```',
                    "operationId": "get_managed_licenses_hierarchy_licenses_post",
                    "parameters": [
                        {
                            "required": False,
                            "schema": {"type": "string", "title": "Order By"},
                            "name": "order_by",
                            "in": "query",
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HierarchiesSchema"
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CustomizedPage_LicenseManagedSchema_"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
            "/hierarchy/licenses/{license_id}": {
                "post": {
                    "tags": ["Hierarchy"],
                    "summary": "Get Managed License By Uuid",
                    "description": 'Route for getting all the licenses in the hierarchy of a given user that they have\ncreated.\n\n### Example Bearer Token structure\n```\n{\n    "iss": "https://acc.bettermarks.com/ucm",\n    "exp": 1701789570.99798,\n    "sub": "12@EN_test",\n    "iat": 1701788970.99799,\n    "jti": "2b47ca46-28b9-4b8d-bd1c-a893acb9de29",\n    "hashes": {\n        "memberships": {\n            "alg": "SHA256",\n            "hash": "86f8b8313c183b3f9ee74b9c042ee440b894f690e9f6308de3da63fd4a6b8"\n        }\n    }\n}\n```',
                    "operationId": "get_managed_license_by_uuid_hierarchy_licenses__license_id__post",
                    "parameters": [
                        {
                            "required": True,
                            "schema": {"type": "string", "title": "License Id"},
                            "name": "license_id",
                            "in": "path",
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/HierarchiesSchema"
                                }
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LicenseManagedSchema"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
            "/hierarchy/licenses/entity-license": {
                "put": {
                    "tags": ["Hierarchy"],
                    "summary": "Get Active License For Entity",
                    "description": 'The "active license for entity" route for a given entity, that is\nthe license taken from the set of \'valid\' licenses (see above route\n`/{entity_type}/{entity_eid}/valid-licenses`), that has the\n- minimum owner level\n- (for same owner level) maximum number of free seats\n\n### Example Bearer Token structure\n```\n{\n    "iss": "https://acc.bettermarks.com/ucm",\n    "exp": 1701789570.99798,\n    "sub": "12@EN_test",\n    "iat": 1701788970.99799,\n    "jti": "2b47ca46-28b9-4b8d-bd1c-a893acb9de29",\n    "hashes": {\n        "memberships": {\n            "alg": "SHA256",\n            "hash": "86f8b8313c183b3f9ee74b9c042ee440b894f690e9f6308de3da63fd4a6b8"\n        }\n    }\n}\n```',
                    "operationId": "get_active_license_for_entity_hierarchy_licenses_entity_license_put",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EntitySchema"}
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LicenseActiveSchema"
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
            "/hierarchy/licenses/entity-licenses": {
                "put": {
                    "tags": ["Hierarchy"],
                    "summary": "Get Licenses For Entity",
                    "description": "The \"valid licenses for entity\" route for a given entity, that is\n'all licenses, that are currently not expired and that are owned by\nsome ancestor of a given entity or by the entity itself'.",
                    "operationId": "get_licenses_for_entity_hierarchy_licenses_entity_licenses_put",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EntitySchema"}
                            }
                        },
                        "required": True,
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "items": {
                                            "$ref": "#/components/schemas/LicenseValidSchema"
                                        },
                                        "type": "array",
                                        "title": "Response Get Licenses For Entity Hierarchy Licenses Entity Licenses Put",
                                    }
                                }
                            },
                        },
                        "422": {
                            "description": "Validation Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HTTPValidationError"
                                    }
                                }
                            },
                        },
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
            "/order/licenses": {
                "post": {
                    "tags": ["Order"],
                    "summary": "Purchase License",
                    "description": "The 'purchase a license' route\n:param token_data: info gotten from ordering token\n:returns: some params of the created license or some error\n          message in case of an error",
                    "operationId": "purchase_license_order_licenses_post",
                    "responses": {
                        "201": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/LicenseCreatedSchema"
                                    }
                                }
                            },
                        }
                    },
                    "security": [{"CustomHTTPBearer": []}],
                }
            },
        },
        "components": {
            "schemas": {
                "CustomizedPage_LicenseAvailableSchema_": {
                    "properties": {
                        "items": {
                            "items": {
                                "$ref": "#/components/schemas/LicenseAvailableSchema"
                            },
                            "type": "array",
                            "title": "Items",
                        },
                        "total": {"type": "integer", "minimum": 0.0, "title": "Total"},
                        "page": {"type": "integer", "minimum": 1.0, "title": "Page"},
                        "size": {"type": "integer", "minimum": 1.0, "title": "Size"},
                        "pages": {"type": "integer", "minimum": 0.0, "title": "Pages"},
                        "links": {"$ref": "#/components/schemas/Links"},
                    },
                    "type": "object",
                    "required": ["items", "links"],
                    "title": "CustomizedPage[LicenseAvailableSchema]",
                },
                "CustomizedPage_LicenseCompleteSchema_": {
                    "properties": {
                        "items": {
                            "items": {
                                "$ref": "#/components/schemas/LicenseCompleteSchema"
                            },
                            "type": "array",
                            "title": "Items",
                        },
                        "total": {"type": "integer", "minimum": 0.0, "title": "Total"},
                        "page": {"type": "integer", "minimum": 1.0, "title": "Page"},
                        "size": {"type": "integer", "minimum": 1.0, "title": "Size"},
                        "pages": {"type": "integer", "minimum": 0.0, "title": "Pages"},
                        "links": {"$ref": "#/components/schemas/Links"},
                    },
                    "type": "object",
                    "required": ["items", "links"],
                    "title": "CustomizedPage[LicenseCompleteSchema]",
                },
                "CustomizedPage_LicenseManagedSchema_": {
                    "properties": {
                        "items": {
                            "items": {
                                "$ref": "#/components/schemas/LicenseManagedSchema"
                            },
                            "type": "array",
                            "title": "Items",
                        },
                        "total": {"type": "integer", "minimum": 0.0, "title": "Total"},
                        "page": {"type": "integer", "minimum": 1.0, "title": "Page"},
                        "size": {"type": "integer", "minimum": 1.0, "title": "Size"},
                        "pages": {"type": "integer", "minimum": 0.0, "title": "Pages"},
                        "links": {"$ref": "#/components/schemas/Links"},
                    },
                    "type": "object",
                    "required": ["items", "links"],
                    "title": "CustomizedPage[LicenseManagedSchema]",
                },
                "EntitySchema": {
                    "properties": {
                        "entity_type": {"type": "string", "title": "Entity Type"},
                        "entity_eid": {"type": "string", "title": "Entity Eid"},
                        "hierarchies": {
                            "items": {},
                            "type": "array",
                            "title": "Hierarchies",
                        },
                    },
                    "type": "object",
                    "required": ["entity_type", "entity_eid", "hierarchies"],
                    "title": "EntitySchema",
                },
                "HTTPValidationError": {
                    "properties": {
                        "detail": {
                            "items": {"$ref": "#/components/schemas/ValidationError"},
                            "type": "array",
                            "title": "Detail",
                        }
                    },
                    "type": "object",
                    "title": "HTTPValidationError",
                },
                "HierarchiesSchema": {
                    "properties": {},
                    "type": "object",
                    "title": "HierarchiesSchema",
                },
                "LicenseActiveSchema": {
                    "properties": {
                        "uuid": {"type": "string", "format": "uuid", "title": "Uuid"},
                        "product_eid": {"type": "string", "title": "Product Eid"},
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "nof_free_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Free Seats",
                            "description": "The absolute number of free seats for a license. `-1` means unlimited.",
                        },
                        "nof_occupied_seats": {
                            "type": "integer",
                            "title": "Nof Occupied Seats",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                            "default": 0,
                        },
                        "is_trial": {"type": "boolean", "title": "Is Trial"},
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                        "owner_eids": {
                            "items": {"type": "string"},
                            "type": "array",
                            "title": "Owner Eids",
                        },
                    },
                    "type": "object",
                    "required": [
                        "uuid",
                        "product_eid",
                        "owner_level",
                        "owner_type",
                        "nof_seats",
                        "nof_free_seats",
                        "nof_occupied_seats",
                        "is_trial",
                        "valid_from",
                        "valid_to",
                        "owner_eids",
                    ],
                    "title": "LicenseActiveSchema",
                },
                "LicenseAvailableSchema": {
                    "properties": {
                        "uuid": {"type": "string", "format": "uuid", "title": "Uuid"},
                        "product_eid": {"type": "string", "title": "Product Eid"},
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "nof_free_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Free Seats",
                            "description": "The absolute number of free seats for a license. `-1` means unlimited.",
                        },
                        "nof_occupied_seats": {
                            "type": "integer",
                            "title": "Nof Occupied Seats",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                            "default": 0,
                        },
                        "is_trial": {"type": "boolean", "title": "Is Trial"},
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                        "owner_eids": {
                            "items": {"type": "string"},
                            "type": "array",
                            "title": "Owner Eids",
                        },
                        "seats": {
                            "items": {"$ref": "#/components/schemas/SeatSchema"},
                            "type": "array",
                            "title": "Seats",
                        },
                    },
                    "type": "object",
                    "required": [
                        "uuid",
                        "product_eid",
                        "owner_level",
                        "owner_type",
                        "nof_seats",
                        "nof_free_seats",
                        "nof_occupied_seats",
                        "is_trial",
                        "valid_from",
                        "valid_to",
                        "owner_eids",
                        "seats",
                    ],
                    "title": "LicenseAvailableSchema",
                },
                "LicenseCompleteSchema": {
                    "properties": {
                        "uuid": {"type": "string", "format": "uuid", "title": "Uuid"},
                        "product_eid": {"type": "string", "title": "Product Eid"},
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "nof_free_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Free Seats",
                            "description": "The absolute number of free seats for a license. `-1` means unlimited.",
                        },
                        "nof_occupied_seats": {
                            "type": "integer",
                            "title": "Nof Occupied Seats",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                            "default": 0,
                        },
                        "is_trial": {"type": "boolean", "title": "Is Trial"},
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                        "id": {"type": "integer", "title": "Id"},
                        "manager_eid": {"type": "string", "title": "Manager Eid"},
                        "owner_eids": {
                            "items": {"type": "string"},
                            "type": "array",
                            "title": "Owner Eids",
                        },
                        "notes": {"type": "string", "title": "Notes"},
                        "seats": {
                            "items": {"$ref": "#/components/schemas/SeatSchema"},
                            "type": "array",
                            "title": "Seats",
                        },
                        "released_seats": {
                            "items": {"$ref": "#/components/schemas/SeatSchema"},
                            "type": "array",
                            "title": "Released Seats",
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Created At",
                        },
                        "updated_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Updated At",
                        },
                    },
                    "type": "object",
                    "required": [
                        "uuid",
                        "product_eid",
                        "owner_level",
                        "owner_type",
                        "nof_seats",
                        "nof_free_seats",
                        "nof_occupied_seats",
                        "is_trial",
                        "valid_from",
                        "valid_to",
                        "id",
                        "manager_eid",
                        "owner_eids",
                        "seats",
                        "released_seats",
                        "created_at",
                    ],
                    "title": "LicenseCompleteSchema",
                },
                "LicenseCreateSchema": {
                    "properties": {
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                        },
                        "product_eid": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Product Eid",
                        },
                        "hierarchy_provider_uri": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Hierarchy Provider Uri",
                        },
                        "owner_eids": {
                            "items": {
                                "type": "string",
                                "maxLength": 256,
                                "minLength": 1,
                            },
                            "type": "array",
                            "title": "Owner Eids",
                        },
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                        "order_id": {
                            "type": "string",
                            "maxLength": 36,
                            "minLength": 0,
                            "title": "Order Id",
                        },
                        "manager_eid": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Manager Eid",
                        },
                        "notes": {
                            "type": "string",
                            "maxLength": 4096,
                            "title": "Notes",
                        },
                    },
                    "type": "object",
                    "required": [
                        "owner_level",
                        "owner_type",
                        "product_eid",
                        "hierarchy_provider_uri",
                        "owner_eids",
                        "valid_from",
                        "valid_to",
                        "manager_eid",
                    ],
                    "title": "LicenseCreateSchema",
                    "description": "Admin license creation.",
                },
                "LicenseCreatedSchema": {
                    "properties": {
                        "uuid": {"type": "string", "format": "uuid", "title": "Uuid"},
                        "product_eid": {"type": "string", "title": "Product Eid"},
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "nof_free_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Free Seats",
                            "description": "The absolute number of free seats for a license. `-1` means unlimited.",
                        },
                        "nof_occupied_seats": {
                            "type": "integer",
                            "title": "Nof Occupied Seats",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                            "default": 0,
                        },
                        "is_trial": {"type": "boolean", "title": "Is Trial"},
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                    },
                    "type": "object",
                    "required": [
                        "uuid",
                        "product_eid",
                        "owner_level",
                        "owner_type",
                        "nof_seats",
                        "nof_free_seats",
                        "nof_occupied_seats",
                        "is_trial",
                        "valid_from",
                        "valid_to",
                    ],
                    "title": "LicenseCreatedSchema",
                },
                "LicenseManagedSchema": {
                    "properties": {
                        "uuid": {"type": "string", "format": "uuid", "title": "Uuid"},
                        "product_eid": {"type": "string", "title": "Product Eid"},
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "nof_free_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Free Seats",
                            "description": "The absolute number of free seats for a license. `-1` means unlimited.",
                        },
                        "nof_occupied_seats": {
                            "type": "integer",
                            "title": "Nof Occupied Seats",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                            "default": 0,
                        },
                        "is_trial": {"type": "boolean", "title": "Is Trial"},
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                        "owner_eids": {
                            "items": {"type": "string"},
                            "type": "array",
                            "title": "Owner Eids",
                        },
                        "seats": {
                            "items": {"$ref": "#/components/schemas/SeatSchema"},
                            "type": "array",
                            "title": "Seats",
                        },
                        "released_seats": {
                            "items": {"$ref": "#/components/schemas/SeatSchema"},
                            "type": "array",
                            "title": "Released Seats",
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Created At",
                        },
                    },
                    "type": "object",
                    "required": [
                        "uuid",
                        "product_eid",
                        "owner_level",
                        "owner_type",
                        "nof_seats",
                        "nof_free_seats",
                        "nof_occupied_seats",
                        "is_trial",
                        "valid_from",
                        "valid_to",
                        "owner_eids",
                        "seats",
                        "released_seats",
                        "created_at",
                    ],
                    "title": "LicenseManagedSchema",
                },
                "LicenseTrialSchema": {
                    "properties": {
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                        },
                        "product_eid": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Product Eid",
                        },
                        "owner_eid": {"type": "string", "title": "Owner Eid"},
                        "memberships": {
                            "items": {},
                            "type": "array",
                            "title": "Memberships",
                        },
                        "duration_weeks": {
                            "type": "integer",
                            "title": "Duration Weeks",
                        },
                    },
                    "type": "object",
                    "required": [
                        "owner_level",
                        "owner_type",
                        "product_eid",
                        "owner_eid",
                        "memberships",
                    ],
                    "title": "LicenseTrialSchema",
                },
                "LicenseUpdateSchema": {
                    "properties": {
                        "manager_eid": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Manager Eid",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                        },
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                    },
                    "type": "object",
                    "title": "LicenseUpdateSchema",
                    "description": "Admin license update.",
                },
                "LicenseValidSchema": {
                    "properties": {
                        "uuid": {"type": "string", "format": "uuid", "title": "Uuid"},
                        "product_eid": {"type": "string", "title": "Product Eid"},
                        "owner_level": {"type": "integer", "title": "Owner Level"},
                        "owner_type": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "Owner Type",
                        },
                        "nof_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Seats",
                            "description": "The absolute number of seats for a license that can be occupied. `-1` means unlimited.",
                        },
                        "nof_free_seats": {
                            "type": "integer",
                            "minimum": -1.0,
                            "title": "Nof Free Seats",
                            "description": "The absolute number of free seats for a license. `-1` means unlimited.",
                        },
                        "nof_occupied_seats": {
                            "type": "integer",
                            "title": "Nof Occupied Seats",
                        },
                        "extra_seats": {
                            "type": "integer",
                            "minimum": 0.0,
                            "title": "Extra Seats",
                            "description": "Extra seats make it possible to “overbook” the license seats of a license.",
                            "default": 0,
                        },
                        "is_trial": {"type": "boolean", "title": "Is Trial"},
                        "valid_from": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid From",
                        },
                        "valid_to": {
                            "type": "string",
                            "format": "date",
                            "title": "Valid To",
                        },
                        "owner_eids": {
                            "items": {"type": "string"},
                            "type": "array",
                            "title": "Owner Eids",
                        },
                    },
                    "type": "object",
                    "required": [
                        "uuid",
                        "product_eid",
                        "owner_level",
                        "owner_type",
                        "nof_seats",
                        "nof_free_seats",
                        "nof_occupied_seats",
                        "is_trial",
                        "valid_from",
                        "valid_to",
                        "owner_eids",
                    ],
                    "title": "LicenseValidSchema",
                },
                "Links": {
                    "properties": {
                        "first": {
                            "type": "string",
                            "title": "First",
                            "example": "/api/v1/users?limit=1&offset1",
                        },
                        "last": {
                            "type": "string",
                            "title": "Last",
                            "example": "/api/v1/users?limit=1&offset1",
                        },
                        "self": {
                            "type": "string",
                            "title": "Self",
                            "example": "/api/v1/users?limit=1&offset1",
                        },
                        "next": {
                            "type": "string",
                            "title": "Next",
                            "example": "/api/v1/users?limit=1&offset1",
                        },
                        "prev": {
                            "type": "string",
                            "title": "Prev",
                            "example": "/api/v1/users?limit=1&offset1",
                        },
                    },
                    "type": "object",
                    "title": "Links",
                },
                "MembershipsSchema": {
                    "properties": {
                        "memberships": {
                            "items": {},
                            "type": "array",
                            "title": "Memberships",
                        }
                    },
                    "type": "object",
                    "required": ["memberships"],
                    "title": "MembershipsSchema",
                    "examples": [
                        {
                            "memberships": [
                                {
                                    "eid": "1@DE_bettermarks",
                                    "name": "Cypress test class 11",
                                    "type": "class",
                                    "level": "1",
                                }
                            ]
                        }
                    ],
                },
                "SeatSchema": {
                    "properties": {
                        "user_eid": {
                            "type": "string",
                            "maxLength": 256,
                            "minLength": 1,
                            "title": "User Eid",
                        },
                        "occupied_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Occupied At",
                        },
                        "last_accessed_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Last Accessed At",
                        },
                        "is_occupied": {"type": "boolean", "title": "Is Occupied"},
                        "status": {"$ref": "#/components/schemas/SeatStatus"},
                    },
                    "type": "object",
                    "required": [
                        "user_eid",
                        "occupied_at",
                        "last_accessed_at",
                        "is_occupied",
                        "status",
                    ],
                    "title": "SeatSchema",
                },
                "SeatStatus": {
                    "enum": ["ACTIVE", "EXPIRED", "NOT_A_MEMBER"],
                    "title": "SeatStatus",
                    "description": "A custom Enum type representing our 'seat status'",
                },
                "ValidationError": {
                    "properties": {
                        "loc": {
                            "items": {
                                "anyOf": [{"type": "string"}, {"type": "integer"}]
                            },
                            "type": "array",
                            "title": "Location",
                        },
                        "msg": {"type": "string", "title": "Message"},
                        "type": {"type": "string", "title": "Error Type"},
                    },
                    "type": "object",
                    "required": ["loc", "msg", "type"],
                    "title": "ValidationError",
                },
            },
            "securitySchemes": {
                "CustomHTTPBearer": {"type": "http", "scheme": "bearer"}
            },
        },
    }


@pytest.fixture()
def admin__licenses():
    return {
        "items": [
            {
                "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "manager_eid": "string",
                "product_eid": "string",
                "owner_level": 0,
                "owner_type": "string",
                "nof_seats": 0,
                "nof_free_seats": 0,
                "nof_occupied_seats": 0,
                "extra_seats": 0,
                "is_trial": True,
                "valid_from": "2023-12-31",
                "valid_to": "2023-12-31",
                # todo: potential error ["string"]
                "owner_eids": "string",
                "notes": "string",
                "id": 0,
                "seats": [
                    {
                        "user_eid": "string",
                        "occupied_at": "2023-12-31 23:59:59",
                        "last_accessed_at": "2023-12-31 23:59:59",
                        "is_occupied": True,
                        "status": "ACTIVE",
                    }
                ],
                "released_seats": [
                    {
                        "user_eid": "string",
                        "occupied_at": "2023-12-31 23:59:59",
                        "last_accessed_at": "2023-12-31 23:59:59",
                        "is_occupied": True,
                        "status": "ACTIVE",
                    }
                ],
                "created_at": "2023-12-31 23:59:59",
                "updated_at": "2023-12-31 23:59:59",
            }
        ],
        "total": 0,
        "page": 0,
        "size": 0,
        "pages": 0,
        "links": {
            "first": "string",
            "last": "string",
            "self": "string",
            "next": "string",
            "prev": "string",
        },
    }


@pytest.fixture()
def admin__licenses__422():
    return {
        "detail": [
            {
                "loc": [],
                "msg": "string",
                "type": "string",
            },
        ],
    }


@pytest.fixture()
def admin__licenses__license():
    return {
        "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "product_eid": "string",
        "owner_level": 0,
        "owner_type": "string",
        "nof_seats": 0,
        "nof_free_seats": 0,
        "nof_occupied_seats": 0,
        "extra_seats": 0,
        "is_trial": True,
        "valid_from": "2023-12-31",
        "valid_to": "2023-12-31",
        "id": 0,
        "manager_eid": "string",
        "owner_eids": "string",
        "notes": "string",
        "seats": [
            {
                "user_eid": "string",
                "occupied_at": "2023-12-31 23:59:59",
                "last_accessed_at": "2023-12-31 23:59:59",
                "is_occupied": True,
                "status": "ACTIVE",
            }
        ],
        "released_seats": [
            {
                "user_eid": "string",
                "occupied_at": "2023-12-31 23:59:59",
                "last_accessed_at": "2023-12-31 23:59:59",
                "is_occupied": True,
                "status": "ACTIVE",
            }
        ],
        "created_at": "2023-12-31 23:59:59",
        "updated_at": "2023-12-31 23:59:59",
    }


@pytest.fixture()
def admin__licenses__delete():
    return "string"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "request_path,request_method,request_status,request_body,exp_status_code,exp_result_fixture",
    [
        ("/admin/licenses", "get", 200, None, 200, "admin__licenses"),
        ("/admin/licenses", "get", 422, None, 422, "admin__licenses__422"),
        (
            "/admin/licenses/license-obj-uuid",
            "get",
            200,
            None,
            200,
            "admin__licenses__license",
        ),
        (
            "/admin/licenses/license-obj-uuid",
            "delete",
            200,
            None,
            200,
            "admin__licenses__delete",
        ),
    ],
)
async def test__example_openapi_response__parametrized(
    request,
    openapi_schema,
    request_path,
    request_method,
    request_status,
    request_body,
    exp_status_code,
    exp_result_fixture,
):
    """Test for `get_mock_response_from()` function."""
    result_status_code, result_example = await example_openapi_response(
        openapi_schema, request_path, request_method, request_body, request_status
    )
    assert result_status_code == exp_status_code
    assert result_example == request.getfixturevalue(exp_result_fixture)


@pytest.fixture()
def openapi_schema_simple() -> dict:
    return {
        "paths": {
            "/test/path": {"get": {}, "post": {}},
            "/test/path/{parameter}": {"get": {}, "post": {}},
        }
    }


@pytest.fixture()
def openapi_schema_simple_mapping() -> dict:
    return {
        "^/test/path$": {"get": {}, "post": {}},
        "^/test/path/[a-zA-Z0-9-_]+$": {"get": {}, "post": {}},
    }


def test__build_regex_paths_map__parametrized(
    openapi_schema_simple, openapi_schema_simple_mapping
):
    """Test for `build_regex_paths()` function."""
    result_mapping = build_regex_paths_map(openapi_schema_simple)
    assert result_mapping == openapi_schema_simple_mapping


@pytest.mark.parametrize(
    "response_schema,exp_raises,exp_result",
    [
        (
            {"anyOf": [{"$ref": "$/some/path/expectedResult"}, {"type": "null"}]},
            False,
            "expectedResult",
        ),
        ({"$ref": "$/some/path/expectedResult"}, False, "expectedResult"),
        ({"$ref": "expectedResult"}, False, "expectedResult"),
        ({"$ref": ""}, False, ""),
        ({"test": "key"}, ValueError, None),
    ],
)
def test__extract_schema_name__parametrized(response_schema, exp_raises, exp_result):
    """Test for `extract_schema_name()` function."""
    if exp_raises:
        with pytest.raises(exp_raises):
            extract_schema_name(response_schema)
    else:
        assert extract_schema_name(response_schema) == exp_result


@pytest.mark.parametrize(
    "response_schema,exp_raises",
    [
        ({"$ref": "#/components/schemas/NonExistingSchema"}, ValueError),
        (
            {"$ref": "#/components/schemas/CustomizedPage_LicenseAvailableSchema_"},
            False,
        ),
    ],
)
def test__extract_schema__parametrized(openapi_schema, response_schema, exp_raises):
    """Test for `extract_schema()` function."""
    if exp_raises:
        with pytest.raises(exp_raises):
            extract_schema(openapi_schema, response_schema)
    else:
        schemas_map, schema_name, schema_dict = extract_schema(
            openapi_schema, response_schema
        )
        assert schemas_map == openapi_schema["components"]["schemas"]
        assert schema_dict == openapi_schema["components"]["schemas"][schema_name]


@pytest.mark.parametrize(
    "request_path,request_method,request_body,exp_raises",
    [
        (
            "/order/licenses",
            "post",
            {},
            None,
        ),
        (
            "/order/licenses",
            "post",
            {"unexpected": "value"},
            ValueError,
        ),
        (
            "/member/licenses/trial",
            "post",
            {
                "owner_level": 0,
                "owner_type": "string",
                "nof_seats": 0,
                "extra_seats": 0,
                "product_eid": "string",
                "owner_eid": "string",
                "memberships": ["string"],
                "duration_weeks": 0,
            },
            None,
        ),
        (
            "/member/licenses/trial",
            "post",
            {
                "owner_level": "0",
                "owner_type": "string",
                "nof_seats": 0,
                "extra_seats": 0,
                "product_eid": "string",
                "owner_eid": "string",
                "memberships": ["string"],
                "duration_weeks": 0,
            },
            ValueError,
        ),
    ],
)
def test__validate_request_body__parametrized(
    openapi_schema, request_path, request_method, request_body, exp_raises
):
    """Test for `validate_request_body()` function."""
    preferred_spec = openapi_schema["paths"][request_path]
    if exp_raises:
        with pytest.raises(exp_raises):
            validate_request_body(
                openapi_schema, request_method, request_body, preferred_spec
            )
    else:
        validate_request_body(
            openapi_schema, request_method, request_body, preferred_spec
        )
