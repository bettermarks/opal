local("make dist", dir="k8s")

k8s_yaml("k8s/dist/namespace.k8s.yaml")
k8s_yaml([f for f in listdir(os.path.join("k8s", "dist")) if not "namespace" in f])

k8s_resource(
    objects=[
        "licensing:namespace",
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
        dockerfile=os.path.join("k8s", "Dockerfile.dev"),
        build_args={"python_version": python_version},
    )


def build_remote():
    build_info = decode_json(
        local(
            "curl -s https://licensing-{}.bettermarks.com/version".format(SEGMENT),
            quiet=True,
        )
    )
    version = build_info["version"]
    print("Use remote version {}".format(version))
    docker_build(
        "licensing",
        ".",
        dockerfile_contents="FROM 676249682729.dkr.ecr.eu-central-1.amazonaws.com/licensing:{}".format(
            version
        ),
    )


SEGMENT = os.getenv("OPAL_SEGMENT", "loc00")
BUILD_LOCAL = SEGMENT.startswith("loc")

if BUILD_LOCAL:
    build_local()
else:
    build_remote()
