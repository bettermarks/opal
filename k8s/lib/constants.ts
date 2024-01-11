import { NodeSelector } from "./types";

export const APP_NODE_POOL_LABELS: NodeSelector = {
  nodetype: "application",
};

/**
 * Name of the secret which is used by service chart to look up application secret.
 * This secret is created by AWS Secrets helper in bm-operations project. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const APPLICATION_SECRET = "licensing-secret";
/**
 * Name of the secret which is used by service chart to look up Postgres DB credentials.
 * This secret is created  by AWS Secrets helper in bm-operations project. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const POSTGRES_SECRET = "licensing-postgres-secret";
/**
 * Name of the secret used by Service Account to pull image from AWS ECR registry.
 * This secret is created by AWS Registry Helper Cron. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const REGISTRY_CREDENTIALS = "registry-credentials";
/**
 * Name of the secret which is used by Licensing service chart to look up licensing service private key.
 * This secret is created by AWS Secrets helper in bm-operations project. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const LICENSING_SERVICE_PRIVATE_KEY = "licensing-service-private-key";
/**
 * Name of the secret which is used by Licensing service chart to look up licensing service private key.
 * This secret is created by AWS Secrets helper in bm-operations project. https://github.com/bettermarks/bm-operations/blob/master/cdk8s/apps/licensing.ts
 */
export const SHOP_SERVICE_PRIVATE_KEY = "shop-service-private-key";

/**
 * Name of various secrets used for event export
 */
export const MONGO_ATLAS_READONLY_SECRET = "mongo-atlas-readonly-secret";
export const DATA_EVENT_API_SECRET = "data-event-api-secret";
export const BACKEND_SECRET = "backend-secret";
export const SDWH_POSTGRES_SECRET = "sdwh-postgres-secret";
export const SDWH_HOST_PRIVATE_KEY = "sdwh-host-private-key";
export const SDWH_PRIVATE_IP = "sdwh-private-ip";

/**
 * Name of the image used for postgres database.
 */
export const POSTGRES_IMAGE = "postgres:14";
/**
 * Name of the ingress class for Licensing which is used in:
 * - k8s/lib/charts/ingress-nginx.ts: Helm -> ingressClassResource
 * - k8s/lib/charts/licensing.ts: KubeIngress -> ingressClassName
 * This prevents clashes in ingress networking with overlapping ingress rules.
 */
export const LICENSING_INGRESS_CLASS = "licensing-nginx";
