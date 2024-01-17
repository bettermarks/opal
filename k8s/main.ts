import { App } from "cdk8s";
import { IngressNginxChart } from "./lib/charts/ingress-nginx";
import { PostgresChart } from "./lib/charts/postgres";
import { LicensingChart } from "./lib/charts/licensing";
import { Segment } from "./lib/types";
import { DEPLOYMENT_CONFIG, APPLICATION_CONFIG } from "./lib/config";
import {
  APP_NODE_POOL_LABELS,
  APPLICATION_SECRET,
  LICENSING_SERVICE_PRIVATE_KEY,
  POSTGRES_IMAGE,
  POSTGRES_SECRET,
  SHOP_SERVICE_PRIVATE_KEY,
  REGISTRY_CREDENTIALS,
  MONGO_ATLAS_READONLY_SECRET,
  DATA_EVENT_API_SECRET,
  BACKEND_SECRET,
  SDWH_POSTGRES_SECRET,
  SDWH_PRIVATE_IP,
  SDWH_HOST_PRIVATE_KEY,
} from "./lib/constants";
import { Namespace } from "./lib/types";
import { MigrationJobChart } from "./lib/charts/migration-job";
import { LicensingServiceAccount } from "./lib/service-account";
import { LicensingConfig } from "./lib/licensing-configmap";
import { EventExportCronJob } from "./lib/charts/event-export-cron-job";

const SEGMENT = (process.env.SEGMENT as Segment) || Segment.LOC00;
const IMAGE_TAG = process.env.IMAGE_TAG || "";
const IMAGE_NAME = "licensing";
const IMAGE_REPO = `676249682729.dkr.ecr.eu-central-1.amazonaws.com/${IMAGE_NAME}`;

const app = new App();

const licensingServiceAccount = new LicensingServiceAccount(
  app,
  "licensing-service-account",
  {
    namespace: Namespace.LICENSING,
    name: "licensing",
    imagePullSecrets: SEGMENT === Segment.LOC00 ? [] : [REGISTRY_CREDENTIALS],
  },
);

const config = new LicensingConfig(app, "licensing-config", {
  namespace: Namespace.LICENSING,
  name: "licensing-config",
  appConfig: APPLICATION_CONFIG[SEGMENT],
});

if (SEGMENT === Segment.LOC00) {
  const pgChart = new PostgresChart(app, "postgres", {
    namespace: Namespace.LICENSING,
    image: POSTGRES_IMAGE,
    name: "licensing-db",
  });
  new MigrationJobChart(app, "migration", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    image: IMAGE_NAME,
    configMap: config.configMap.name,
    postgresSecret: pgChart.secret.name,
    applicationSecret: "loc00-application-secret",
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
  });
  new LicensingChart(app, "licensing", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    applicationSecret: "loc00-application-secret",
    configMap: config.configMap.name,
    image: IMAGE_NAME,
    licensingServicePrivateKey: "loc00-licensing-service-private-key",
    postgresSecret: pgChart.secret.name,
    segment: SEGMENT,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
    shopServicePrivateKey: "loc00-shop-service-private-key",
  });
  new IngressNginxChart(app, "ingress-nginx", {
    namespace: Namespace.LICENSING,
    replicas: 1,
    tlsSecret: "loc00-tls-secret",
  });
  new EventExportCronJob(app, "event-export", {
    namespace: Namespace.LICENSING,
    name: "licensing-event-export",
    configMap: config.configMap.name,
    image: IMAGE_NAME,
    mongoAtlasReadonlySecret: undefined,
    postgresSecret: pgChart.secret.name,
    eventApiSecret: "loc00-data-event-api-secret",
    sdwhPostgresSecret: "loc00-sdwh-postgres-secret",
    sdwhHostPrivateKey: "loc00-sdwh-host-private-key",
    sdwhPrivateIp: "loc00-sdwh-private-ip",
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
  });
} else {
  new MigrationJobChart(app, "migration", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    image: `${IMAGE_REPO}:${IMAGE_TAG}`,
    configMap: config.configMap.name,
    postgresSecret: POSTGRES_SECRET,
    applicationSecret: APPLICATION_SECRET,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
    nodeSelector: APP_NODE_POOL_LABELS,
  });
  new LicensingChart(app, "licensing", {
    namespace: Namespace.LICENSING,
    name: "licensing",
    apiResources: DEPLOYMENT_CONFIG[SEGMENT].apiResources,
    apiReplicas: DEPLOYMENT_CONFIG[SEGMENT].apiReplicas,
    applicationSecret: APPLICATION_SECRET,
    configMap: config.configMap.name,
    image: `${IMAGE_REPO}:${IMAGE_TAG}`,
    licensingServicePrivateKey: LICENSING_SERVICE_PRIVATE_KEY,
    postgresSecret: POSTGRES_SECRET,
    nodeSelector: APP_NODE_POOL_LABELS,
    segment: SEGMENT,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
    shopServicePrivateKey: SHOP_SERVICE_PRIVATE_KEY,
  });
  new EventExportCronJob(app, "event-export", {
    backendSecret: BACKEND_SECRET,
    configMap: config.configMap.name,
    eventApiSecret: DATA_EVENT_API_SECRET,
    image: `${IMAGE_REPO}:${IMAGE_TAG}`,
    logformat: 'json',
    name: "licensing-event-export",
    namespace: Namespace.LICENSING,
    mongoAtlasReadonlySecret: MONGO_ATLAS_READONLY_SECRET,
    nodeSelector: APP_NODE_POOL_LABELS,
    postgresSecret: POSTGRES_SECRET,
    resources: DEPLOYMENT_CONFIG[SEGMENT].eventExportResources,
    sdwhPostgresSecret: SDWH_POSTGRES_SECRET,
    sdwhHostPrivateKey: SDWH_HOST_PRIVATE_KEY,
    sdwhPrivateIp: SDWH_PRIVATE_IP,
    serviceAccountName: licensingServiceAccount.serviceAccount.name,
  })
}

app.synth();
