import {
  EnvFromSource,
  JobTemplateSpec,
  KubeCronJob,
  ResourceRequirements,
} from "../../imports/k8s";
import { EVENT_EXPORT_SECRET } from "../constants";
import { NodeSelector } from "../types";
import { Chart, ChartProps } from "cdk8s";
import { ImagePullPolicy, RestartPolicy } from "cdk8s-plus-29";
import { Construct } from "constructs";

interface EventExportProps extends ChartProps {
  /**
   * Name for resources in this chart
   *
   * @default event-export
   */
  name?: string;
  /**
   * Name of the config map containing necessary configuration.
   * Keys are derived from the type ApplicationConfig
   */
  configMap: string;
  /**
   * Docker image with AWS CLI and kubectl
   *
   * @see https://hub.docker.com/r/bettermarks/aws-cli-kubectl
   */
  image: string;
  /**
   * The logformat to use. Possible values: "console", "json"
   */
  logFormat?: string;
  /**
   * Node selector
   */
  nodeSelector?: NodeSelector;
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
      configMap,
      image,
      logFormat = "console",
      nodeSelector,
      resources,
      serviceAccountName,
    } = props;

    const applicationEnv: EnvFromSource[] = [
      {
        configMapRef: {
          name: configMap,
        },
      },
      {
        secretRef: {
          name: EVENT_EXPORT_SECRET,
        },
      },
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
                command: [
                  "python",
                  "src/services/licensing/scripts/export_events.py",
                  "--events-per-run=12000",
                  `--log-format=${logFormat}`,
                ],
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
