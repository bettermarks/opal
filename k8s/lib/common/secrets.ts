import {
  ExternalSecretV1Beta1,
  ExternalSecretV1Beta1SpecDataRemoteRefDecodingStrategy,
} from "../../imports/external-secrets.io";
import {
  ESO_STACKIT_SECRETS_MANAGER,
  EVENT_EXPORT_SECRET,
  LICENSING_SECRET,
  LOCAL_POSTGRES_ENV_DATA,
} from "../constants";
import { getStageFromSegment, Segment } from "../types";
import { Chart, ChartProps } from "cdk8s";
import { Secret } from "cdk8s-plus-29";
import { Construct } from "constructs";

interface LicensingSecretsProps extends ChartProps {
  /**
   * Segment.
   */
  segment: Segment;
  /**
   * Namespace.
   */
  namespace: string;
}

export class LicensingSecrets extends Chart {
  constructor(scope: Construct, id: string, props: LicensingSecretsProps) {
    super(scope, id, props);

    const { segment, namespace } = props;

    if (segment === Segment.LOC00) {
      new Secret(this, "local-licensing-secret", {
        metadata: {
          name: LICENSING_SECRET,
          namespace,
        },
        stringData: {
          APM_SECRET_TOKEN: "",
          LICENSING_SERVICE_KID: "f72e2e28-a232-411c-a5ad-34a18480aa10",
          LICENSING_SERVICE_PRIVATE_KEY: [
            "-----BEGIN PRIVATE KEY-----",
            "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgrCkyWdmYFh6plKVx",
            "gypQFWoVJ1LOOBdr+36LhulS85ShRANCAAQ5nWN+SnvwJ4Xt2z9EtJl1BkUjWFY5",
            "PuM88BLOTlEjn6Win2uqSn5JdFVPsn7r9h+O9HAnrSBWUaNRghpkVwuZ",
            "-----END PRIVATE KEY-----",
          ].join("\n"),
          ...LOCAL_POSTGRES_ENV_DATA,
        },
      });
      new Secret(this, "local-event-export-secret", {
        metadata: {
          name: EVENT_EXPORT_SECRET,
          namespace,
        },
        stringData: {
          SDWH_POSTGRES_SECRET: "",
          SDWH_HOST_PRIVATE_KEY: "",
          SDWH_PRIVATE_IP: "127.0.0.1",
          DATA_EVENT_API_KEY: "",
          MONGODB_URI: "",
          DATA_EVENT_API_SECRET: "",
          ...LOCAL_POSTGRES_ENV_DATA,
        },
      });
    } else {
      /**
       * Create a K8s secrets from multiple secrets.
       */
      new ExternalSecretV1Beta1(this, "external-licensing-secret", {
        metadata: {
          name: `ext-${LICENSING_SECRET}`,
          namespace,
        },
        spec: {
          refreshInterval: "1h", // "0" means: fetch data and create secret only once.
          secretStoreRef: {
            name: ESO_STACKIT_SECRETS_MANAGER,
            kind: "ClusterSecretStore",
          },
          target: {
            name: LICENSING_SECRET,
          },
          // Fetch all key-value pairs from key-value-secrets.
          dataFrom: [
            {
              extract: {
                key: `stackit/${segment}-pg-cluster-licensing/credentials`,
              },
            },
            {
              extract: {
                key: `licensing/${segment}/credentials`,
              },
            },
          ],
          /**
           * STACKIT: Secrets Manager (Vault) only supports key-value secrets.
           * In this case the value is Base64 encoded for PEM formatted secrets,
           * eg.: private or public key
           */
          data: [
            {
              secretKey: "LICENSING_SERVICE_PRIVATE_KEY",
              remoteRef: {
                key: `licensing/${segment}/licensing-service-private-key`,
                property: "LICENSING_SERVICE_PRIVATE_KEY",
                decodingStrategy:
                  ExternalSecretV1Beta1SpecDataRemoteRefDecodingStrategy.BASE64,
              },
            },
          ],
        },
      });

      new ExternalSecretV1Beta1(this, "external-event-export-secret", {
        metadata: {
          name: `ext-${EVENT_EXPORT_SECRET}`,
          namespace,
        },
        spec: {
          refreshInterval: "1h", // "0" means: fetch data and create secret only once.
          secretStoreRef: {
            name: ESO_STACKIT_SECRETS_MANAGER,
            kind: "ClusterSecretStore",
          },
          target: {
            name: EVENT_EXPORT_SECRET,
          },
          // Fetch all key-value pairs from key-value-secrets.
          dataFrom: [
            {
              extract: {
                key: `stackit/${segment}-pg-cluster-licensing/credentials`,
              },
            },
            ...(segment === Segment.PRO00
              ? [
                  {
                    extract: {
                      // This secret contains the public IP in pro00 STACKIT vault.
                      key: `ionos/${segment}-sdwh/private-ip`,
                    },
                  },
                ]
              : []),
          ],
          data: [
            ...(segment === Segment.PRO00
              ? [
                  /**
                   * STACKIT: Secrets Manager (Vault) only supports key-value secrets.
                   * In this case the value is Base64 encoded for PEM formatted secrets,
                   * eg.: private or public key
                   */
                  {
                    secretKey: "SDWH_HOST_PRIVATE_KEY",
                    remoteRef: {
                      key: `ionos/${segment}-sdwh/rsa-private-key`,
                      property: "SDWH_HOST_PRIVATE_KEY",
                      decodingStrategy:
                        ExternalSecretV1Beta1SpecDataRemoteRefDecodingStrategy.BASE64,
                    },
                  },
                  {
                    secretKey: "SDWH_POSTGRES_SECRET",
                    remoteRef: {
                      key: `ionos/${segment}-sdwh/reader-password`,
                      property: "SDWH_POSTGRES_SECRET",
                    },
                  },
                  {
                    secretKey: "DATA_EVENT_API_KEY",
                    remoteRef: {
                      key: `${getStageFromSegment(segment)}_event_api_key_secret`,
                      property: "DATA_EVENT_API_KEY",
                    },
                  },
                ]
              : []),
            {
              // Fetch a specific key from a key-value secret.
              secretKey: "BM_ENCRYPTION_PASSWORD",
              remoteRef: {
                key: `backend/${segment}/credentials`,
                property: "BM_ENCRYPTION_PASSWORD",
              },
            },
            {
              // Fetch a specific key from a key-value secret.
              secretKey: "MONGODB_URI",
              remoteRef: {
                key: `stackit/${segment}/application/readonly-secret`,
                property: "MONGODB_URI",
              },
            },
          ],
        },
      });
    }
  }
}
