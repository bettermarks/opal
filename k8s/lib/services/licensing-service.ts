import { ServiceType } from "cdk8s-plus-27";
import { Construct } from "constructs";
import {
  KubeDeployment,
  KubeService,
  Container,
  IntOrString,
  Volume,
  TopologySpreadConstraint,
} from "../../imports/k8s";
import { NodeSelector } from "../types";

export type LicensingServiceProps = {
  name: string;
  replicas: number;
  serviceAccountName: string;
  nodeSelector?: NodeSelector;
  initContainers: Container[];
  containers: Container[];
  volumes?: Volume[];
  servicePort: number;
  containerPort: number;
  namespace?: string;
};
export class LicensingService extends Construct {
  readonly service?: KubeService;

  constructor(scope: Construct, id: string, props: LicensingServiceProps) {
    super(scope, id);

    const {
      containerPort,
      containers,
      initContainers,
      name,
      namespace,
      nodeSelector,
      replicas,
      serviceAccountName,
      servicePort,
      volumes,
    } = props;

    /**
     * Node selector and topology spread constraints
     */
    let topologySpreadConstraints: TopologySpreadConstraint[] = [];
    if (nodeSelector && Object.keys(nodeSelector).length > 0) {
      topologySpreadConstraints = [
        {
          maxSkew: 1,
          topologyKey: "kubernetes.io/hostname",
          whenUnsatisfiable: "DoNotSchedule",
          labelSelector: {
            matchLabels: {
              app: name,
            },
          },
        },
      ];
    }

    new KubeDeployment(this, `${name}-deployment`, {
      metadata: {
        name: name,
        namespace,
      },
      spec: {
        replicas: replicas,
        selector: {
          matchLabels: {
            app: name,
          },
        },
        template: {
          metadata: {
            labels: {
              app: name,
            },
          },
          spec: {
            serviceAccountName,
            nodeSelector,
            ...(topologySpreadConstraints.length > 0 && {
              topologySpreadConstraints: topologySpreadConstraints,
            }),
            initContainers,
            containers,
            ...(volumes && { volumes: volumes }),
          },
        },
      },
    });

    this.service = new KubeService(this, name, {
      metadata: {
        name,
        namespace,
      },
      spec: {
        type: ServiceType.CLUSTER_IP,
        ports: [
          {
            port: servicePort,
            targetPort: IntOrString.fromNumber(containerPort),
          },
        ],
        selector: {
          app: name,
        },
      },
    });
  }
}
