import { ConfigMap } from "cdk8s-plus-27";
import { Construct } from "constructs";
import { ApplicationConfig } from "./types";
import { Chart, ChartProps } from "cdk8s";

export type LicensingConfigProps = ChartProps & {
  name: string;
  appConfig: ApplicationConfig;
  namespace?: string;
};

export class LicensingConfig extends Chart {
  readonly configMap: ConfigMap;

  constructor(scope: Construct, id: string, props: LicensingConfigProps) {
    super(scope, id);
    const { name, namespace, appConfig } = props;

    this.configMap = new ConfigMap(this, name, {
      metadata: {
        name,
        namespace,
      },
    });
    for (const [key, value] of Object.entries(appConfig)) {
      if (
        Array.isArray(value) ||
        typeof value === "boolean" ||
        typeof value === "object"
      ) {
        this.configMap.addData(key, JSON.stringify(value));
      } else {
        this.configMap.addData(key, value);
      }
    }
  }
}
