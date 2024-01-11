import { Chart, ChartProps } from "cdk8s";
import { HttpIngressPathType, ImagePullPolicy } from "cdk8s-plus-27";
import { Construct } from "constructs";
import {
  EnvFromSource,
  IntOrString,
  KubeIngress,
  ResourceRequirements,
} from "../../imports/k8s";
import { LICENSING_INGRESS_CLASS } from "../constants";

import { LicensingService } from "../services/licensing-service";
import { Namespace, NodeSelector, Segment } from "../types";

/**
 * This class is the implementation detail of Licensing deployment.
 */
export type LicensingChartProps = ChartProps & {
  /**
   * Docker image for Licensing
   */
  image: string;
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
   * Name of the secret containing necessary credentials for running the service.
   *
   * Required keys:
   * - APM_SECRET_TOKEN
   * - LICENSING_SERVICE_KID
   * - SHOP_SERVICE_KID (will be outsourced to shop service)
   * - SHOP_INVOICE_AUTH_PASSWORD (will be outsourced to shop service)
   */
  applicationSecret?: string;
  /**
   * Name of the secret containing the licensing service private key.
   *
   * Required key:
   * - LICENSING_SERVICE_PRIVATE_KEY
   */
  licensingServicePrivateKey?: string;
  /**
   * Name of the secret containing the shop service private key.
   *
   * Required key:
   * - SHOP_SERVICE_PRIVATE_KEY
   */
  shopServicePrivateKey?: string;
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
 * Deploys Licensing server.
 */
export class LicensingChart extends Chart {
  constructor(scope: Construct, id: string, props: LicensingChartProps) {
    super(scope, id, props);

    const {
      namespace = Namespace.LICENSING,
      apiReplicas = 1,
      apiResources,
      applicationSecret,
      licensingServicePrivateKey,
      shopServicePrivateKey,
      image,
      nodeSelector,
      postgresSecret,
      segment,
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
          name: postgresSecret,
        },
      },
      {
        secretRef: {
          name: licensingServicePrivateKey,
        },
      },
      {
        secretRef: {
          name: shopServicePrivateKey,
        },
      },
      ...(applicationSecret
        ? [
            {
              secretRef: {
                name: applicationSecret,
              },
            },
          ]
        : []),
    ];

    const apiName = `${name}-api`;
    const licensingService = new LicensingService(this, `${apiName}-service`, {
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
              path: "/v1/status",
            },
            initialDelaySeconds: 10,
          },
          livenessProbe: {
            httpGet: {
              port: IntOrString.fromNumber(8000),
              path: "/v1/status",
            },
            initialDelaySeconds: 10,
          },
        },
      ],
      servicePort: 80,
      containerPort: 8000,
    });

    if (segment === Segment.LOC00) {
      /**
       * Create ingress
       */
      new KubeIngress(this, `${name}-ingress`, {
        metadata: {
          name: `${name}-ingress`,
          namespace,
          annotations: {
            "nginx.ingress.kubernetes.io/enable-cors": "true",
            "nginx.ingress.kubernetes.io/cors-allow-origin":
              "https://apps.bettermarks.loc",
          },
        },
        spec: {
          ingressClassName: LICENSING_INGRESS_CLASS,
          rules: [
            {
              http: {
                paths: [
                  {
                    path: "/",
                    pathType: HttpIngressPathType.PREFIX,
                    backend: {
                      service: {
                        name: licensingService.service!.name,
                        port: {
                          number: 80,
                        },
                      },
                    },
                  },
                ],
              },
            },
          ],
        },
      });
    }
  }
}
