import { PostgresChart } from "../lib/postgres/postgres";
import { Testing } from "cdk8s";

describe("postgres-chart", () => {
  test("should match with snapshot", () => {
    const app = Testing.app();
    const chart = new PostgresChart(app, "test-chart", {
      image: "postgres:14",
      name: "licensing-db",
      namespace: "dummy-namespace",
    });
    const results = Testing.synth(chart);
    expect(results).toMatchSnapshot();
  });
});
