import {
  EnvFromSource,
  Quantity,
  ResourceRequirements,
} from "../../imports/k8s";
import { LicensingJob } from "../common/licensing-job";
import { LICENSING_SECRET, POSTGRES_IMAGE } from "../constants";
import { NodeSelector, Namespace } from "../types";
import { Chart, ChartProps } from "cdk8s";
import { ImagePullPolicy } from "cdk8s-plus-29";
import { Construct } from "constructs";

/**
 * This class is the implementation detail of Licensing deployment.
 */
export type LicensingChartProps = ChartProps & {
  /**
   * Docker image for Licensing
   */
  image: string;
  name: string;
  serviceAccountName: string;
  /**
   * Name of the config map containing necessary configuration.
   * Keys are derived from the type ApplicationConfig
   */
  configMap: string;
  nodeSelector?: NodeSelector;
  migrationJobResources?: ResourceRequirements;
};

export class MigrationJobChart extends Chart {
  constructor(scope: Construct, id: string, props: LicensingChartProps) {
    super(scope, id, props);

    const {
      namespace = Namespace.LICENSING,
      image,
      nodeSelector,
      migrationJobResources,
      serviceAccountName,
      name,
      configMap,
    } = props;

    const applicationEnv: EnvFromSource[] = [
      {
        configMapRef: {
          name: configMap,
        },
      },
      {
        secretRef: {
          name: LICENSING_SECRET,
        },
      },
    ];
    /**
     * Job for running database migration
     */
    new LicensingJob(this, "migrate", {
      name: `${name}-migration`,
      namespace,
      nodeSelector: nodeSelector,
      serviceAccountName,
      ttlSecondsAfterFinished: 60,
      initContainers: [
        {
          name: "wait-for-database-migration",
          image: POSTGRES_IMAGE,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: [
            "sh",
            "-c",
            "until pg_isready --host ${DB_HOST}; do sleep 1; done",
          ],
          envFrom: applicationEnv,
          resources: {
            requests: {
              cpu: Quantity.fromNumber(0.1),
              memory: Quantity.fromString("64Mi"),
            },
            limits: {
              memory: Quantity.fromString("64Mi"),
            },
          },
        },
      ],
      containers: [
        {
          name: "licensing-migration",
          image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          command: ["bash", "-c"],
          args: ["alembic upgrade head"],
          envFrom: applicationEnv,
          resources: migrationJobResources,
        },
      ],
    });
  }
}
