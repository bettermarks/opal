import { KubeIngress } from "../../imports/k8s";
import { Chart, ChartProps } from "cdk8s";
import { HttpIngressPathType } from "cdk8s-plus-29";
import { Construct } from "constructs";

export type LocalIngressProps = ChartProps & {};

export class LocalIngressChart extends Chart {
  constructor(scope: Construct, id: string, props: LocalIngressProps) {
    const { namespace } = props;

    super(scope, id, props);

    /**
     * Create ingress
     */
    new KubeIngress(this, "local-ingress", {
      metadata: {
        namespace,
        name: "licensing-ingress",
      },
      spec: {
        ingressClassName: "loc00-nginx",
        rules: [
          {
            host: "licensing.bettermarks.loc",
            http: {
              paths: [
                {
                  path: "/",
                  pathType: HttpIngressPathType.PREFIX,
                  backend: {
                    service: {
                      name: "licensing-api",
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
