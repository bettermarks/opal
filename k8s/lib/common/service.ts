import {
  Container,
  IntOrString,
  KubeDeployment,
  KubeService,
  Toleration,
  TopologySpreadConstraint,
  Volume,
} from "../../imports/k8s";
import { DEFAULT_TOLERATIONS } from "../constants";
import { NodeSelector } from "../types";
import { ServiceType } from "cdk8s-plus-29";
import { Construct } from "constructs";

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
     * Node selector, tolerations and topology spread constraints
     */
    let tolerations: Toleration[] | undefined;
    let topologySpreadConstraints: TopologySpreadConstraint[] | undefined;
    if (nodeSelector && Object.keys(nodeSelector).length > 0) {
      tolerations = DEFAULT_TOLERATIONS;
      topologySpreadConstraints = [
        {
          maxSkew: 1,
          topologyKey: "topology.kubernetes.io/zone",
          whenUnsatisfiable: "ScheduleAnyway",
          labelSelector: {
            matchLabels: {
              app: name,
            },
          },
          matchLabelKeys: ["pod-template-hash"],
          nodeAffinityPolicy: "Honor",
          nodeTaintsPolicy: "Honor",
        },
        {
          maxSkew: 1,
          topologyKey: "kubernetes.io/hostname",
          whenUnsatisfiable: "ScheduleAnyway",
          labelSelector: {
            matchLabels: {
              app: name,
            },
          },
          matchLabelKeys: ["pod-template-hash"],
          nodeAffinityPolicy: "Honor",
          nodeTaintsPolicy: "Honor",
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
        strategy: {
          rollingUpdate: {
            maxSurge: IntOrString.fromNumber(1),
            maxUnavailable: IntOrString.fromNumber(0),
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
            tolerations,
            topologySpreadConstraints,
            initContainers,
            containers,
            volumes,
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
