import { Container, KubeJob } from "../../imports/k8s";
import { NodeSelector } from "../types";
import { RestartPolicy } from "cdk8s-plus-29";
import { Construct } from "constructs";

export type LicensingJobProps = {
  name: string;
  namespace: string;
  ttlSecondsAfterFinished: number;
  nodeSelector?: NodeSelector;
  serviceAccountName: string;
  initContainers: Container[];
  containers: Container[];
};

export class LicensingJob extends Construct {
  readonly job: KubeJob;
  constructor(scope: Construct, id: string, props: LicensingJobProps) {
    super(scope, id);
    /**
     * Node selector
     */
    let nodeSelector: { [key: string]: string } = {};
    if (props.nodeSelector) {
      nodeSelector[nodeSelector.nodeLabelKey] = nodeSelector.nodeLabelValue;
    }

    this.job = new KubeJob(this, `${props.name}`, {
      metadata: {
        name: props.name,
        namespace: props.namespace,
      },
      spec: {
        backoffLimit: 1, // number of retries
        ttlSecondsAfterFinished: props.ttlSecondsAfterFinished, // delete job after specified time has finished
        template: {
          spec: {
            serviceAccountName: props.serviceAccountName,
            nodeSelector: nodeSelector,
            restartPolicy: RestartPolicy.NEVER,
            initContainers: props.initContainers,
            containers: props.containers,
          },
        },
      },
    });
  }
}
