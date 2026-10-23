local("make dist", dir="k8s")

# Create namespace if it doesn't exist
local("kubectl get namespace integration --no-headers || kubectl create namespace integration")
k8s_yaml(listdir(os.path.join("k8s", "dist")))

k8s_resource(
    objects=[
        "licensing:serviceaccount:licensing",
        "licensing:role:licensing",
        "licensing:rolebinding:licensing",
        "licensing-config:configmap:licensing",
        "licensing-db-init-db-script:configmap:licensing",
        "licensing:secret:licensing",
        "event-export:secret:licensing",
        "licensing-ingress:ingress:licensing",
    ],
    new_name="licensing:k8s",
    labels="licensing",
)
k8s_resource(
    "licensing-db",
    labels="licensing",
    resource_deps=["licensing:k8s"],
    port_forwards=["15432:5432"],
)
k8s_resource("licensing-migration", labels="licensing", resource_deps=["licensing-db"])
# k8s_resource("licensing-api", labels="licensing", resource_deps=["licensing-migration"], port_forwards=['8000:8000'])
k8s_resource("licensing-api", labels="licensing", resource_deps=["licensing-migration"])
k8s_resource(
    "licensing-event-export",
    labels="licensing",
    resource_deps=["licensing-migration"],
    auto_init=False,
    trigger_mode=TRIGGER_MODE_MANUAL,
)


def build_local():
    python_version = str(read_file(".python-version")).strip("\n")
    docker_build(
        "licensing",
        ".",
        dockerfile=os.path.join("k8s", "Dockerfile"),
        build_args={"python_version": python_version},
    )


SEGMENT = os.getenv("OPAL_SEGMENT", "loc00")

build_local()
