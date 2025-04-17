import { LocalIngressChart } from "../lib/common/local-ingress";
import { Testing } from "cdk8s";

describe("ingress-nginx-chart", () => {
  test("with tls", () => {
    const app = Testing.app();
    const chart = new LocalIngressChart(app, "test-chart", {
      namespace: "dummy-namespace",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
