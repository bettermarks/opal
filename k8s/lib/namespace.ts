import { Chart, App } from "cdk8s";
import * as kplus from "cdk8s-plus-29";

export const createNamespaceChart = (app: App, name: string) => {
  const namespaceChart = new Chart(app, "namespace");
  new kplus.Namespace(namespaceChart, "Namespace", {
    metadata: { name: name },
  });

  return namespaceChart;
};
