import { Chart, ChartProps } from "cdk8s";
import { Construct } from "constructs";
import {
  EnvFromSource,
  JobTemplateSpec,
  KubeCronJob,
  ResourceRequirements,
} from "../../imports/k8s";
import { ImagePullPolicy, RestartPolicy } from "cdk8s-plus-27";
import { NodeSelector } from "../types";

interface EventExportProps extends ChartProps {
  /**
   * Name for resources in this chart
   *
   * @default event-export
   */
  name?: string;
  /**
   * Name of the secret containing the Backend credentials.
   *
   * Required key:
   * - BM_ENCRYPTION_PASSWORD
   */
  backendSecret?: string;
  /**
   * Name of the config map containing necessary configuration.
   * Keys are derived from the type ApplicationConfig
   */
  configMap: string;
  /**
   * Name of the secret containing the Event service API key.
   *
   * Required key:
   * -EVENT_API_SECRET
   */
  eventApiSecret?: string;
  /**
   * Docker image with AWS CLI and kubectl
   *
   * @see https://hub.docker.com/r/bettermarks/aws-cli-kubectl
   */
  image: string;
  /**
   * The logformat to use. Possible values: "console", "json"
   */
  logformat?: string;
  /**
   * Name of the secret containing the Mongo Atlas Credentials.
   *
   * Required key:
   * - MONGODB_URI
   */
  mongoAtlasReadonlySecret?: string;
  /**
   * Node selector
   */
  nodeSelector?: NodeSelector;
  /**
   * Name of the secret containing Postgres credentials
   *
   * Required keys:
   * - DB_HOST
   * - DB_PORT
   * - DB_USER
   * - DB_PASSWORD
   * - DB_NAME
   */
  postgresSecret: string;
  /**
   * Name of the secret containing the SDWH SSH host private key.
   *
   * Required key:
   * - SDWH_HOST_PRIVATE_KEY
   */
  sdwhHostPrivateKey?: string;
  /**
   * Name of the secret containing the SDWH credentials.
   *
   * Required key:
   * - SDWH_PRIVATE_IP
   */
  sdwhPrivateIp?: string;
  /**
   * Name of the secret containing the SDWH readonly user password.
   *
   * Required key:
   * - SDWH_POSTGRES_SECRET
   */
  sdwhPostgresSecret?: string;
  serviceAccountName: string;
  resources?: ResourceRequirements;
}

/**
 * This chart runs the event export as cron job.
 */
export class EventExportCronJob extends Chart {
  constructor(scope: Construct, id: string, props: EventExportProps) {
    super(scope, id, props);
    const {
      namespace,
      name = "licensing-event-export",
      backendSecret,
      configMap,
      eventApiSecret,
      image,
      logformat = "console",
      mongoAtlasReadonlySecret,
      nodeSelector,
      postgresSecret,
      resources,
      serviceAccountName,
      sdwhHostPrivateKey,
      sdwhPostgresSecret,
      sdwhPrivateIp,
    } = props;

    const applicationEnv: EnvFromSource[] = [
      {
        configMapRef: {
          name: configMap,
        },
      },
      {
        secretRef: {
          name: postgresSecret,
        },
      },
      ...(sdwhHostPrivateKey
        ? [
          {
            secretRef: {
              name: sdwhHostPrivateKey,
            },
          },
        ]
        : []),
      ...(sdwhPostgresSecret
        ? [
          {
            secretRef: {
              name: sdwhPostgresSecret,
            },
          },
        ]
        : []),
      ...(eventApiSecret
        ? [
          {
            secretRef: {
              name: eventApiSecret,
            },
          },
        ]
        : []),
      ...(backendSecret
        ? [
          {
            secretRef: {
              name: backendSecret,
            },
          },
        ]
        : []),
      ...(mongoAtlasReadonlySecret
        ? [
          {
            secretRef: {
              name: mongoAtlasReadonlySecret,
            },
          },
        ]
        : []),
      ...(sdwhPrivateIp
        ? [
          {
            secretRef: {
              name: sdwhPrivateIp,
            },
          },
        ]
        : []),
    ];

    const jobTemplate: JobTemplateSpec = {
      metadata: {
        name,
        namespace,
      },
      spec: {
        suspend: false,
        backoffLimit: 1, // retry
        ttlSecondsAfterFinished: 600, // delete finished job after 10 min
        template: {
          spec: {
            nodeSelector,
            serviceAccountName,
            restartPolicy: RestartPolicy.NEVER,
            containers: [
              {
                name,
                image,
                imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
                resources,
                envFrom: applicationEnv,
                command: ["python", "src/services/licensing/scripts/export_events.py", "--events-per-run=3000", `--log-format=${logformat}`],
              },
            ],
          },
        },
      },
    };

    new KubeCronJob(this, "cronjob", {
      metadata: {
        name,
        namespace,
      },
      spec: {
        schedule: "*/20 * * * *",
        concurrencyPolicy: "Forbid",
        jobTemplate,
        suspend: false,
      },
    });
  }
}
