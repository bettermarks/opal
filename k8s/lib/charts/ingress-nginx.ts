import { Chart, ChartProps, Helm } from "cdk8s";
import { ServiceType } from "cdk8s-plus-27";
import { TopologySpreadConstraint } from "../../imports/k8s";
import { Construct } from "constructs";
import { Namespace, NodeSelector } from "../types";
import { LICENSING_INGRESS_CLASS } from "../constants";

export interface IngressNginxChartProps extends ChartProps {
  /**
   * Ingress Nginx chart version
   * @default 4.3.0
   */
  version?: string;
  /**
   * Node selector config
   */
  nodeSelector?: NodeSelector;
  /**
   * Replicas
   * @default 3
   */
  replicas?: number;
  /**
   * TLS secret
   */
  tlsSecret?: string;
}

/**
 * Deploys Nginx Ingress controller
 *
 * Following defaults are set for resources:
 * - controller.resources.requests.cpu   : "100m"
 * - controller.resources.requests.memory: "90Mi"
 */
export class IngressNginxChart extends Chart {
  constructor(scope: Construct, id: string, props: IngressNginxChartProps) {
    super(scope, id, props);

    const {
      version = "4.4.2",
      namespace = Namespace.LICENSING,
      nodeSelector,
      replicas = 3,
      tlsSecret,
    } = props;

    /**
     * TLS configuration for local dev
     */
    let extraArgs = {};
    if (tlsSecret) {
      extraArgs = { "default-ssl-certificate": `${namespace}/${tlsSecret}` };
    }

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
              app: "nginx-controller",
            },
          },
        },
      ];
    }

    new Helm(this, "ingress-nginx", {
      chart: "ingress-nginx",
      releaseName: "ingress-nginx",
      helmFlags: [
        "--repo",
        "https://kubernetes.github.io/ingress-nginx",
        "--version",
        version,
        "--namespace",
        namespace,
      ],
      values: {
        controller: {
          ingressClassResource: {
            name: LICENSING_INGRESS_CLASS,
            controllerValue: `k8s.io/${LICENSING_INGRESS_CLASS}`,
          },
          service: {
            type: ServiceType.CLUSTER_IP,
          },
          config: {
            "use-forwarded-headers": true,
            "log-format-escape-json": true,
            "log-format-upstream":
              '{ "timestamp": "$time_iso8601", "nginx": {"x_forwarded_proto": "$http_x_forwarded_proto", "x_forwarded_for": "$proxy_add_x_forwarded_for", "remote_addr": "$remote_addr", "remote_user": "$remote_user", "status": "$status", "body_bytes_sent": $body_bytes_sent, "request": "$request", "request_length": $request_length, "request_method": "$request_method", "request_time": $request_time, "http_referrer": "$http_referer", "http_user_agent": "$http_user_agent", "upstream_connect_time": $upstream_connect_time, "upstream_response_time": $upstream_response_time, "upstream_bytes_sent": $upstream_bytes_sent, "upstream_bytes_received": $upstream_bytes_received, "upstream_status": "$upstream_status", "upstream_server": "$upstream_addr", "host": "$host", "cf_ray": "$http_cf_ray", "request_id": "$request_id" } }',
            "worker-processes": "auto",
          },
          replica: replicas,
          nodeSelector: nodeSelector,
          labels: {
            app: "nginx-controller",
          },
          ...(topologySpreadConstraints.length > 0 && {
            topologySpreadConstraints: topologySpreadConstraints,
          }),
          extraArgs,
        },
      },
    });
  }
}
