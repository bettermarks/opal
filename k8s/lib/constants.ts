import { Toleration } from "../imports/k8s";
import { NodeSelector } from "./types";

export const APP_NODE_POOL_LABELS: NodeSelector = {
  nodetype: "application",
};

// Default tolerations
export const DEFAULT_TOLERATIONS: Toleration[] = [
  {
    key: "node.kubernetes.io/unreachable",
    operator: "Exists",
    effect: "NoExecute",
    tolerationSeconds: 20,
  },
  {
    key: "node.kubernetes.io/not-ready",
    operator: "Exists",
    effect: "NoExecute",
    tolerationSeconds: 20,
  },
];

/**
 * Name of the secret which is used by LicensingChart and MigrationJobChart to look up secrets.
 */
export const LICENSING_SECRET = "licensing";
/**
 * Name of the secret which is used by EventExportCronJob chart to look up secrets.
 */
export const EVENT_EXPORT_SECRET = "event-export";

/**
 * Name of the secret used by Service Account to pull image from AWS ECR registry.
 * This secret is created as part of a K8s cluster setup in bm-operations repo.
 */
export const REGISTRY_CREDENTIALS = "registry-credentials";

/**
 * Name of the image used for postgres database.
 */
export const POSTGRES_IMAGE = "postgres:14";

/**
 *  Local postgres
 */
export const LOCAL_POSTGRES_ENV_DATA = {
  DB_HOST: "licensing-db",
  DB_PORT: "5432",
  DB_USER: "postgres",
  DB_PASSWORD: "postgres",
  DB_NAME: "postgres",
  POSTGRES_PASSWORD: "postgres",
  POSTGRES_USER: "postgres",
  POSTGRES_DB: "postgres",
};

/**
 * External Secrets Cluster Secret Store: STACKIT Secrets Manager (Vault)
 */
export const ESO_STACKIT_SECRETS_MANAGER = "stackit-secrets-manager";
