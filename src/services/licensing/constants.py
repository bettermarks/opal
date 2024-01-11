# when querying for licenses, these 'order by' fields are valid in
# the order by query parameter
ALLOWED_LICENSE_ORDER_BY_FIELDS = [
    "id",
    "uuid",
    "hierarchy_provider_uri",
    "product_eid",
    "manager_eid",
    "owner_type",
    "owner_level",
    "owner_eids",
    "valid_from",
    "valid_to",
    "nof_seats",
    "is_trial",
    "created_at",
]

ALLOWED_LICENSE_FILTER_RESTRICTIONS = ["manager_eid"]

# internal infinity representation
INFINITE_INT: int = int(1e18)

# infinity representation to the JSON output
INFINITE_INT_JSON: int = -1
