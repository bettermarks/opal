import { IntOrString, KubeDeployment, KubeService } from "../../imports/k8s";
import { LICENSING_SECRET } from "../constants";
import { Namespace } from "../types";
import { Chart, ChartProps } from "cdk8s";
import { ConfigMap, ImagePullPolicy, ServiceType } from "cdk8s-plus-29";
import { Construct } from "constructs";

interface PostgresChartProps extends ChartProps {
  image: string;
  name: string;
}

export class PostgresChart extends Chart {
  constructor(scope: Construct, id: string, props: PostgresChartProps) {
    super(scope, id, props);
    const { name, namespace = Namespace.LICENSING } = props;

    const configMap = new ConfigMap(this, "initdb", {
      metadata: {
        name: `${name}-init-db-script`,
        namespace,
      },
      data: {}, // if you need any init-command put it here...
    });

    new KubeDeployment(this, "pg-deployment", {
      metadata: {
        name,
        namespace,
        labels: {
          app: name,
        },
      },
      spec: {
        selector: {
          matchLabels: {
            app: name,
          },
        },
        replicas: 1,
        template: {
          metadata: {
            labels: {
              app: name,
            },
          },
          spec: {
            containers: [
              {
                name,
                image: props.image,
                imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
                ports: [{ containerPort: 5432 }],
                envFrom: [
                  {
                    secretRef: { name: LICENSING_SECRET },
                  },
                ],
                readinessProbe: {
                  tcpSocket: {
                    port: IntOrString.fromNumber(5432),
                  },
                  initialDelaySeconds: 10,
                },
                livenessProbe: {
                  tcpSocket: {
                    port: IntOrString.fromNumber(5432),
                  },
                  initialDelaySeconds: 10,
                },
                volumeMounts: [
                  {
                    name: `${configMap.name}-volume`,
                    mountPath: "/docker-entrypoint-initdb.d/",
                  },
                ],
              },
            ],
            volumes: [
              {
                name: `${configMap.name}-volume`,
                configMap: {
                  name: configMap.name,
                },
              },
            ],
          },
        },
      },
    });

    new KubeService(this, id, {
      metadata: {
        name,
        namespace,
      },
      spec: {
        type: ServiceType.CLUSTER_IP,
        ports: [
          {
            port: 5432,
          },
        ],
        selector: {
          app: name,
        },
      },
    });
  }
}
