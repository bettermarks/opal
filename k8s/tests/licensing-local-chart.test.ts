import { LicensingChart } from "../lib/licensing/licensing";
import { Segment } from "../lib/types";
import { Testing } from "cdk8s";

describe("licensing-local-chart", () => {
  beforeEach(() => {
    jest.useFakeTimers().setSystemTime(new Date("2008-12-01"));
  });
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new LicensingChart(app, "test-chart", {
      name: "licensing",
      image: "licensing",
      namespace: "dummy-namespace",
      segment: Segment.LOC00,
      configMap: "licensing-configmap",
      serviceAccountName: "dummy-service-account",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
