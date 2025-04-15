import { LocalIngressChart } from "../lib/common/local-ingress";
import { createLicensingApp } from "../lib/licensing/licensing-app";
import { PostgresChart } from "../lib/postgres/postgres";
import { Namespace, Segment } from "../lib/types";
import { Testing } from "cdk8s";

describe(`licensing at ${Segment.LOC00}`, () => {
  const {
    licensingServiceAccount,
    licensingConfig,
    licensingSecrets,
    licensingChart,
    licensingMigrationJob,
    licensingEventExportCronjob,
    pgChart,
    localIngressChart,
  } = createLicensingApp(Testing.app(), {
    imageTag: "latest",
    namespace: Namespace.LICENSING,
    segment: Segment.LOC00,
  });

  it("should match snapshot for licensing migration job", () => {
    expect(Testing.synth(licensingMigrationJob)).toMatchSnapshot();
  });

  it("should not have image pull secret", () => {
    expect(licensingServiceAccount.imagePullSecrets).toHaveLength(0);
  });
  it("should match snapshot for service account", () => {
    expect(Testing.synth(licensingServiceAccount)).toMatchSnapshot();
  });

  it("should match snapshot for configmap", () => {
    expect(Testing.synth(licensingConfig)).toMatchSnapshot();
  });

  it("should match snapshot for licensing chart", () => {
    expect(Testing.synth(licensingChart)).toMatchSnapshot();
  });

  it("should match chart for licensing secrets", () => {
    expect(Testing.synth(licensingSecrets)).toMatchSnapshot();
  });
  it("should match snapshot for licensing event export cronjob", () => {
    expect(Testing.synth(licensingEventExportCronjob)).toMatchSnapshot();
  });

  it("should create pgChart", () => {
    expect(pgChart).toBeDefined();
  });
  it("should match snapshot for mongodb chart", () => {
    expect(Testing.synth(pgChart as PostgresChart)).toMatchSnapshot();
  });

  it("should create local ingress chart", () => {
    expect(localIngressChart).toBeInstanceOf(LocalIngressChart);
  });
  it("should match snapshot for local ingress chart", () => {
    expect(
      Testing.synth(localIngressChart as LocalIngressChart),
    ).toMatchSnapshot();
  });
});

describe.each([
  Segment.DEV00,
  Segment.DEV01,
  Segment.CI00,
  Segment.CI01,
  Segment.PRO00,
])("Licensing at %s", (segment) => {
  const {
    licensingServiceAccount,
    licensingConfig,
    licensingSecrets,
    licensingChart,
    licensingMigrationJob,
    licensingEventExportCronjob,
    pgChart,
    localIngressChart,
  } = createLicensingApp(Testing.app(), {
    imageTag: "latest",
    namespace: Namespace.LICENSING,
    segment,
  });

  it("should match snapshot for licensing migration job", () => {
    expect(Testing.synth(licensingMigrationJob)).toMatchSnapshot();
  });

  it("should have image pull secret", () => {
    expect(licensingServiceAccount.imagePullSecrets).toHaveLength(1);
  });
  it("should match snapshot for service account", () => {
    expect(Testing.synth(licensingServiceAccount)).toMatchSnapshot();
  });

  it("should match snapshot for configmap", () => {
    expect(Testing.synth(licensingConfig)).toMatchSnapshot();
  });

  it("should match snapshot for licensing chart", () => {
    expect(Testing.synth(licensingChart)).toMatchSnapshot();
  });

  it("should match chart for licensing secrets", () => {
    expect(Testing.synth(licensingSecrets)).toMatchSnapshot();
  });
  it("should match snapshot for licensing event export cronjob", () => {
    expect(Testing.synth(licensingEventExportCronjob)).toMatchSnapshot();
  });

  it("should not create pgChart", () => {
    expect(pgChart).toBeUndefined();
  });

  it("should not create local ingress chart", () => {
    expect(localIngressChart).toBeUndefined();
  });
});
