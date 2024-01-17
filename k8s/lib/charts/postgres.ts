import { Chart, ChartProps } from "cdk8s";
import {
  ConfigMap,
  ImagePullPolicy,
  ISecret,
  Secret,
  ServiceType,
} from "cdk8s-plus-27";
import { Construct } from "constructs";
import { Namespace } from "../types";
import { IntOrString, KubeDeployment, KubeService } from "../../imports/k8s";

interface PostgresChartProps extends ChartProps {
  image: string;
  name: string;
}

export class PostgresChart extends Chart {
  /**
   * Secret with Postgres credentials
   *
   * keys:
   * - DB_HOST
   * - DB_PORT
   * - DB_USER
   * - DB_PASSWORD
   * - DB_NAME
   * - POSTGRES_PASSWORD
   */
  readonly secret: ISecret;

  constructor(scope: Construct, id: string, props: PostgresChartProps) {
    super(scope, id, props);
    const { name, namespace = Namespace.LICENSING } = props;
    const pgSecret = new Secret(this, "secret", {
      metadata: {
        name: name,
        namespace,
      },
      stringData: {
        DB_PORT: "5432",
        DB_USER: "postgres",
        DB_PASSWORD: "postgres",
        DB_NAME: "postgres",
        POSTGRES_PASSWORD: "postgres",
        POSTGRES_USER: "postgres",
        POSTGRES_DB: "postgres",
      },
    });

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
                    secretRef: { name: pgSecret.name },
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

    const pgService = new KubeService(this, id, {
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

    pgSecret.addStringData("DB_HOST", pgService.name);
    pgSecret.addStringData("DB_PORT", "5432");
    this.secret = pgSecret;
  }
}
