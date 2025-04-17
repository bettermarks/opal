import { Quantity } from "../../imports/k8s";
import {
  ApplicationConfig,
  DeploymentConfig,
  LogLevel,
  Segment,
} from "../types";

/**
 * Information to go in secrets
 *
 * DB related:
 * - DB_HOST
 * - DB_PORT
 * - DB_USER
 * - DB_PASSWORD
 * - DB_NAME
 *
 * Application related:
 * - APM_SECRET_TOKEN
 * - LICENSING_SERVICE_KID
 * - LICENSING_SERVICE_PRIVATE_KEY
 *
 * Bettermarks event export related:
 * - MONGODB_URI
 * - BM_ENCRYPTION_PASSWORD
 * - DATA_EVENT_API_SECRET
 * - SDWH_POSTGRES_SECRET
 * - SDWH_PRIVATE_IP
 * - SDWH_HOST_PRIVATE_KEY
 /**
 * Information to go in config map
 */
export const APPLICATION_CONFIG: { [key: string]: ApplicationConfig } = {
  [Segment.LOC00]: {
    SEGMENT: Segment.LOC00,
    LOG_FORMAT: "console",
    LOG_LEVEL: LogLevel.DEBUG,
    LICENSING_SERVICE_URL: "https://licensing.bettermarks.loc",
    EVENTS_EXPORT_FUNCTION:
      "services.licensing.export.mock_export.export_event",
    APM_URL: "",
    APM_ENABLED: false,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
    JWT_VERIFICATION_KEYS: {
      "3e94b29d-c4fe-4f19-b627-dcb62f112a01": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF shop service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEPRHRuf4kEGKdYllznwF2w4T6K954\n/ltQbQZmzqDZ6WVhtfGm0ncQyv58E/uIu5UAYl55Nzprhbi+5leVyFsnaQ==\n-----END PUBLIC KEY-----\n",
      },
      "8a210c1b-1020-4835-a0c5-2c0b31c90095": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF hierarchy provider",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEpZa2khO++tAJJWjWXSWVnZ1wGl9P\nQajoLhpNGJGWJmFy4+lYyMC9g/R3ZaoAjYXwbOi2tNl4ROYqWsZGEvmgig==\n-----END PUBLIC KEY-----\n",
      },
      "9aac3057-e492-448e-90bf-1404124056b0": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF ordering service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEldVFYtN5IffED9PrPRHBwFmXHYWK\ngz9Inj/8651FRWekYyWvkdrvWkNRj5OLOpqtWRXFnRjqdxgeUPPJduajLQ==\n-----END PUBLIC KEY-----\n",
      },
      "d31c2005-cd17-4dd3-93fc-0bc07c4318da": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF backoffice service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEzSUdN8X3yf6V4NdhCHsP2mQdcZKA\n+uJWbcPr8YDjBDK4VOCaYm+WV3ce1yKFgqmXYZZEIdz5XIIPw7/zNdiJLQ==\n-----END PUBLIC KEY-----\n",
      },
    },
  },
  [Segment.DEV00]: {
    SEGMENT: Segment.DEV00,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.INFO,
    LICENSING_SERVICE_URL: "https://licensing-dev00.bettermarks.com",
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
    JWT_VERIFICATION_KEYS: {
      "6a8913b1-8e57-436a-9551-0165b5ceaadc": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF shop service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAECK+vuevrAWEJ/pXBlPMfhxlFjT7S\nXX7f8xxa/6T1xuEBXRlaDI/pNWdHHkeFgoM/QOOX8N3gXI32h/J164lnJw==\n-----END PUBLIC KEY-----\n",
      },
      "deb57535-a9b6-437c-8ab0-edd24e888d24": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF hierarchy provider",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEUjGuzKKQf098S+FfEJyw81Bt1z0B\nS5sg2jF0b+tKGRiW4L/6wwLeXxsrCb4192gVxorIarb17o80BTGmMeaNEw==\n-----END PUBLIC KEY-----\n",
      },
      "9aac3057-e492-448e-90bf-1404124056b0": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF ordering service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEldVFYtN5IffED9PrPRHBwFmXHYWK\ngz9Inj/8651FRWekYyWvkdrvWkNRj5OLOpqtWRXFnRjqdxgeUPPJduajLQ==\n-----END PUBLIC KEY-----\n",
      },
      "cd07ca32-7d99-44c9-823e-e6103942767e": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF backoffice service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE3ETb4eEvUXQB9zvpfe3z0slDZ+0c\nF2q3Eb1YTfCnaqE7eHPZ/4SKiwv8TojzJr3+/cImjqFkD4Xie0POo9wLfg==\n-----END PUBLIC KEY-----\n",
      },
    },
  },
  [Segment.DEV01]: {
    SEGMENT: Segment.DEV01,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.INFO,
    LICENSING_SERVICE_URL: "https://licensing-dev01.bettermarks.com",
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
    JWT_VERIFICATION_KEYS: {
      "6a8913b1-8e57-436a-9551-0165b5ceaadc": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF shop service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAECK+vuevrAWEJ/pXBlPMfhxlFjT7S\nXX7f8xxa/6T1xuEBXRlaDI/pNWdHHkeFgoM/QOOX8N3gXI32h/J164lnJw==\n-----END PUBLIC KEY-----\n",
      },
      "deb57535-a9b6-437c-8ab0-edd24e888d24": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF hierarchy provider",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEUjGuzKKQf098S+FfEJyw81Bt1z0B\nS5sg2jF0b+tKGRiW4L/6wwLeXxsrCb4192gVxorIarb17o80BTGmMeaNEw==\n-----END PUBLIC KEY-----\n",
      },
      "9aac3057-e492-448e-90bf-1404124056b0": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF ordering service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEldVFYtN5IffED9PrPRHBwFmXHYWK\ngz9Inj/8651FRWekYyWvkdrvWkNRj5OLOpqtWRXFnRjqdxgeUPPJduajLQ==\n-----END PUBLIC KEY-----\n",
      },
      "cd07ca32-7d99-44c9-823e-e6103942767e": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF backoffice service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE3ETb4eEvUXQB9zvpfe3z0slDZ+0c\nF2q3Eb1YTfCnaqE7eHPZ/4SKiwv8TojzJr3+/cImjqFkD4Xie0POo9wLfg==\n-----END PUBLIC KEY-----\n",
      },
    },
  },
  [Segment.CI00]: {
    SEGMENT: Segment.CI00,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.INFO,
    LICENSING_SERVICE_URL: "https://licensing-ci00.bettermarks.com",
    EVENTS_EXPORT_FUNCTION:
      "services.licensing.export.bettermarks_export.export_event",
    EVENTS_EXPORT_EXPORT_HOOK:
      "services.licensing.export.bettermarks_export.modified_event",
    SDWH_PORT: "22",
    SDWH_USER: "ionos",
    SDWH_DB_HOST: "localhost",
    SDWH_DB_USER: "bmsdwhbiuser",
    SDWH_DB_PORT: "5432",
    SDWH_DB_NAME: "bmsdwh",
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
    JWT_VERIFICATION_KEYS: {
      "794724cc-d956-4009-9eba-46d2aa38eabc": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF shop service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEivNA6e6LoJKM886bFOCxQ7+3F36P\n+6QLxAGtJ5GIQDAQsOpaiKXAVaqJ2nAhGCdJbByzmtRn4nR/t0bU4jCGCA==\n-----END PUBLIC KEY-----\n",
      },
      "bd0bc964-cddf-4705-85ba-8d57be91977c": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF hierarchy provider",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEdlDx9TUME1wIxWNju6ax+RZOlkYO\njDigVFlep5dk30kCynjDYjBp0EsO4bePiyfK913/swEZ/r/CzUc2B7VlcQ==\n-----END PUBLIC KEY-----\n",
      },
      "9aac3057-e492-448e-90bf-1404124056b0": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF ordering service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEldVFYtN5IffED9PrPRHBwFmXHYWK\ngz9Inj/8651FRWekYyWvkdrvWkNRj5OLOpqtWRXFnRjqdxgeUPPJduajLQ==\n-----END PUBLIC KEY-----\n",
      },
      "cec04f88-14cb-442c-94c2-86196e33c926": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF backoffice service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE7jG0Lko1bL1iy0exdlWt6ugJLN/D\n6W79hKhYYiMqu43fJci2Gd3huo6WQG9FrnoIzNIy6+pFbTbtVSuljy0EBQ==\n-----END PUBLIC KEY-----\n",
      },
    },
  },
  [Segment.CI01]: {
    SEGMENT: Segment.CI01,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.INFO,
    LICENSING_SERVICE_URL: "https://licensing-ci01.bettermarks.com",
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
    JWT_VERIFICATION_KEYS: {
      "794724cc-d956-4009-9eba-46d2aa38eabc": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF shop service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEivNA6e6LoJKM886bFOCxQ7+3F36P\n+6QLxAGtJ5GIQDAQsOpaiKXAVaqJ2nAhGCdJbByzmtRn4nR/t0bU4jCGCA==\n-----END PUBLIC KEY-----\n",
      },
      "bd0bc964-cddf-4705-85ba-8d57be91977c": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF hierarchy provider",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEdlDx9TUME1wIxWNju6ax+RZOlkYO\njDigVFlep5dk30kCynjDYjBp0EsO4bePiyfK913/swEZ/r/CzUc2B7VlcQ==\n-----END PUBLIC KEY-----\n",
      },
      "9aac3057-e492-448e-90bf-1404124056b0": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF ordering service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEldVFYtN5IffED9PrPRHBwFmXHYWK\ngz9Inj/8651FRWekYyWvkdrvWkNRj5OLOpqtWRXFnRjqdxgeUPPJduajLQ==\n-----END PUBLIC KEY-----\n",
      },
      "cec04f88-14cb-442c-94c2-86196e33c926": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF backoffice service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE7jG0Lko1bL1iy0exdlWt6ugJLN/D\n6W79hKhYYiMqu43fJci2Gd3huo6WQG9FrnoIzNIy6+pFbTbtVSuljy0EBQ==\n-----END PUBLIC KEY-----\n",
      },
    },
  },
  [Segment.PRO00]: {
    SEGMENT: Segment.PRO00,
    LOG_FORMAT: "json",
    LOG_LEVEL: LogLevel.INFO,
    LICENSING_SERVICE_URL: "https://licensing.bettermarks.com",
    EVENTS_EXPORT_FUNCTION:
      "services.licensing.export.bettermarks_export.export_event",
    EVENTS_EXPORT_EXPORT_HOOK:
      "services.licensing.export.bettermarks_export.modified_event",
    SDWH_PORT: "22",
    SDWH_USER: "ionos",
    SDWH_DB_HOST: "localhost",
    SDWH_DB_USER: "bmsdwhbiuser",
    SDWH_DB_PORT: "5432",
    SDWH_DB_NAME: "bmsdwh",
    DATA_EVENT_API_URL: "https://data.bettermarks.com/events",
    APM_URL: "https://apm.bettermarks.com",
    APM_ENABLED: true,
    APM_TRANSACTION_SAMPLE_RATE: "0.1",
    JWT_VERIFICATION_KEYS: {
      "4b1cc728-5828-4639-8a27-a860dbd87aba": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF shop service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEUzo1cWp0LxhL6xRHUjX9LylocdWK\nCuGlz/Y7+1hawKFPcw7ZoeBCVDHUPYh9TGknnNIQHfkPZguwUUWPz2gpCA==\n-----END PUBLIC KEY-----\n",
      },
      "6a51f17d-7187-4408-a9bb-2c267cf2be78": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF hierarchy provider",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE+TFRZVMMoK3y8ui+hSdLxjtmnwCP\ntHE8J1dsCduCSfhETqq9SgXKDks8KMkeYUmy2ykmWdyAmKydEwizTD4RDw==\n-----END PUBLIC KEY-----\n",
      },
      "9aac3057-e492-448e-90bf-1404124056b0": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF ordering service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEldVFYtN5IffED9PrPRHBwFmXHYWK\ngz9Inj/8651FRWekYyWvkdrvWkNRj5OLOpqtWRXFnRjqdxgeUPPJduajLQ==\n-----END PUBLIC KEY-----\n",
      },
      "72afe436-6b79-43a9-ae04-82d6af25f6ff": {
        format: "pem",
        desc: "used as public (EC) JWS signature key OF backoffice service",
        key: "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE4rQ1KsDrKZ2n5qyQyFRmGuEY8kI6\nx/x5t9ZnIyR96Dwr9uyPU9C5wSENDG95dlSgqgTTGDftBcavsP1DjhcydQ==\n-----END PUBLIC KEY-----",
      },
    },
  },
};

/**
 * Deployment configuration per segment
 */
export const DEPLOYMENT_CONFIG: {
  [key: string]: DeploymentConfig;
} = {
  [Segment.LOC00]: {
    apiReplicas: 1,
    migrationJobResources: {},
    loadFixturesJobResources: {},
    apiResources: {},
    eventExportResources: {},
  },
  [Segment.DEV00]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.025),
        memory: Quantity.fromString("64Mi"),
      },
      limits: {
        memory: Quantity.fromString("64Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.025),
        memory: Quantity.fromString("64Mi"),
      },
      limits: {
        memory: Quantity.fromString("64Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    eventExportResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    apiReplicas: 1,
  },
  [Segment.DEV01]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.025),
        memory: Quantity.fromString("64Mi"),
      },
      limits: {
        memory: Quantity.fromString("64Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.025),
        memory: Quantity.fromString("64Mi"),
      },
      limits: {
        memory: Quantity.fromString("64Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    eventExportResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    apiReplicas: 1,
  },
  [Segment.CI00]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.05),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.05),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(0.25),
        memory: Quantity.fromString("256Mi"),
      },
      limits: {
        memory: Quantity.fromString("256Mi"),
      },
    },
    eventExportResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    apiReplicas: 2,
  },
  [Segment.CI01]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.05),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.05),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(0.25),
        memory: Quantity.fromString("256Mi"),
      },
      limits: {
        memory: Quantity.fromString("256Mi"),
      },
    },
    eventExportResources: {
      requests: {
        cpu: Quantity.fromNumber(0.1),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    apiReplicas: 2,
  },
  [Segment.PRO00]: {
    migrationJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.05),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    loadFixturesJobResources: {
      requests: {
        cpu: Quantity.fromNumber(0.25),
        memory: Quantity.fromString("128Mi"),
      },
      limits: {
        memory: Quantity.fromString("128Mi"),
      },
    },
    apiResources: {
      requests: {
        cpu: Quantity.fromNumber(0.25),
        memory: Quantity.fromString("512Mi"),
      },
      limits: {
        memory: Quantity.fromString("512Mi"),
      },
    },
    eventExportResources: {
      requests: {
        cpu: Quantity.fromNumber(0.3),
        memory: Quantity.fromString("256Mi"),
      },
      limits: {
        memory: Quantity.fromString("256Mi"),
      },
    },
    apiReplicas: 4,
  },
};

export const getAppConfigSegment = (segment: Segment): ApplicationConfig => {
  return {
    ...APPLICATION_CONFIG[segment],
  };
};
