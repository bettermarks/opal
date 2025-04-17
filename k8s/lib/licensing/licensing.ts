import {
  EnvFromSource,
  IntOrString,
  ResourceRequirements,
} from "../../imports/k8s";
import { LicensingService } from "../common/service";
import { LICENSING_SECRET } from "../constants";
import { Namespace, NodeSelector, Segment } from "../types";
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
  serviceAccountName: string;
  segment: Segment;
  name: string;
  /**
   * Name of the config map containing necessary configuration.
   * Keys are derived from the type ApplicationConfig
   */
  configMap: string;
  nodeSelector?: NodeSelector;
  apiResources?: ResourceRequirements;
  /**
   * API replicas
   * @default 3
   */
  apiReplicas?: number;
};

/**
 * Deploys Licensing API server
 */
export class LicensingChart extends Chart {
  constructor(scope: Construct, id: string, props: LicensingChartProps) {
    super(scope, id, props);

    const {
      namespace = Namespace.LICENSING,
      apiReplicas = 1,
      apiResources,
      image,
      nodeSelector,
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

    const apiName = `${name}-api`;
    new LicensingService(this, `${apiName}-service`, {
      name: apiName,
      namespace,
      replicas: apiReplicas,
      serviceAccountName,
      nodeSelector: nodeSelector,
      initContainers: [],
      containers: [
        {
          name: apiName,
          image,
          imagePullPolicy: ImagePullPolicy.IF_NOT_PRESENT,
          ports: [
            {
              containerPort: 8000,
            },
          ],
          resources: apiResources,
          envFrom: applicationEnv,
          readinessProbe: {
            httpGet: {
              port: IntOrString.fromNumber(8000),
              path: "/status",
            },
            timeoutSeconds: 3,
            initialDelaySeconds: 10,
          },
          livenessProbe: {
            httpGet: {
              port: IntOrString.fromNumber(8000),
              path: "/livez",
            },
            timeoutSeconds: 3,
            initialDelaySeconds: 10,
          },
        },
      ],
      servicePort: 80,
      containerPort: 8000,
    });
  }
}
