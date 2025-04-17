import { DEPLOYMENT_CONFIG } from "../lib/common/config";
import { APP_NODE_POOL_LABELS } from "../lib/constants";
import { LicensingChart } from "../lib/licensing/licensing";
import { Segment } from "../lib/types";
import { Testing } from "cdk8s";

const segment = Segment.DEV00;
describe("licensing-chart", () => {
  beforeEach(() => {
    jest.useFakeTimers().setSystemTime(new Date("2008-12-01"));
  });
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new LicensingChart(app, "test-chart", {
      name: "licensing",
      namespace: "dummy-namespace",
      image:
        "676249682729.dkr.ecr.eu-central-1.amazonaws.com/bm-glu:e6b588df29edbf984d876e195bdaee5230c5ad92",
      configMap: "licensing-configmap",
      serviceAccountName: "dummy-service-account",
      nodeSelector: APP_NODE_POOL_LABELS,
      segment: segment,
      apiResources: DEPLOYMENT_CONFIG[segment].apiResources,
      apiReplicas: DEPLOYMENT_CONFIG[segment].apiReplicas,
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
