import { APPLICATION_CONFIG, DEPLOYMENT_CONFIG } from "../common/config";
import { LocalIngressChart } from "../common/local-ingress";
import { LicensingSecrets } from "../common/secrets";
import { LicensingServiceAccount } from "../common/service-account";
import {
  APP_NODE_POOL_LABELS,
  POSTGRES_IMAGE,
  REGISTRY_CREDENTIALS,
} from "../constants";
import { PostgresChart } from "../postgres/postgres";
import { AppSynthProps, Segment } from "../types";
import { LicensingChart } from "./licensing";
import { LicensingConfig } from "./licensing-configmap";
import { EventExportCronJob } from "./licensing-event-export-cron-job";
import { MigrationJobChart } from "./licensing-migration-job";
import { App } from "cdk8s";

export const createLicensingApp = (app: App, appProps: AppSynthProps) => {
  const { segment, imageTag, namespace } = appProps;

  let pgChart: PostgresChart | undefined = undefined;
  let localIngressChart: LocalIngressChart | undefined = undefined;

  const licensingServiceAccount = new LicensingServiceAccount(
    app,
    "licensing-service-account",
    {
      imagePullSecrets: segment === Segment.LOC00 ? [] : [REGISTRY_CREDENTIALS],
      name: "licensing",
      namespace,
    },
  );
  const licensingConfig = new LicensingConfig(app, "licensing-config", {
    appConfig: APPLICATION_CONFIG[segment],
    name: "licensing-config",
    namespace,
  });
  const licensingSecrets = new LicensingSecrets(app, "licensing-secrets", {
    segment,
    namespace,
  });
  const image =
    segment === Segment.LOC00
      ? "licensing"
      : `676249682729.dkr.ecr.eu-central-1.amazonaws.com/licensing:${imageTag}`;
  const nodeSelector =
    segment === Segment.LOC00 ? undefined : APP_NODE_POOL_LABELS;
  const {
    apiResources,
    apiReplicas,
    migrationJobResources,
    eventExportResources,
  } = DEPLOYMENT_CONFIG[segment];

  const licensingChart = new LicensingChart(app, "licensing", {
    name: "licensing",
    image,
    configMap: licensingConfig.configMap.name,
    apiReplicas,
    apiResources,
    namespace,
    nodeSelector,
    segment,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
  });

  const licensingMigrationJob = new MigrationJobChart(app, "migration", {
    configMap: licensingConfig.configMap.name,
    image,
    name: "licensing",
    namespace,
    nodeSelector,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
    migrationJobResources,
  });

  const logFormat = segment === Segment.LOC00 ? "console" : "json";
  const licensingEventExportCronjob = new EventExportCronJob(
    app,
    "event-export",
    {
      configMap: licensingConfig.configMap.name,
      image,
      logFormat,
      name: "licensing-event-export",
      namespace,
      nodeSelector,
      resources: eventExportResources,
      serviceAccountName: licensingServiceAccount.serviceAccount.name,
    },
  );

  if (segment === Segment.LOC00) {
    pgChart = new PostgresChart(app, "postgres", {
      image: POSTGRES_IMAGE,
      name: "licensing-db",
      namespace,
    });
    localIngressChart = new LocalIngressChart(app, "local-ingress", {
      namespace,
    });
  }
  return {
    licensingServiceAccount,
    licensingConfig,
    licensingSecrets,
    licensingChart,
    licensingMigrationJob,
    licensingEventExportCronjob,
    pgChart,
    localIngressChart,
  };
};
