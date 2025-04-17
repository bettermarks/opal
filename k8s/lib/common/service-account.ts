import {
  KubeRole,
  KubeServiceAccount,
  KubeRoleBinding,
} from "../../imports/k8s";
import { Namespace } from "../types";
import { Chart } from "cdk8s";
import { Construct } from "constructs";

export type LicensingServiceAccountProps = {
  /**
   * Secret names for AWS ECR registry
   */
  imagePullSecrets: ReadonlyArray<string>;
  namespace?: string;
  name: string;
};

export class LicensingServiceAccount extends Chart {
  readonly serviceAccount: KubeServiceAccount;
  readonly imagePullSecrets: ReadonlyArray<string>;

  constructor(
    scope: Construct,
    id: string,
    props: LicensingServiceAccountProps,
  ) {
    super(scope, id);

    const { name, namespace = Namespace.LICENSING, imagePullSecrets } = props;

    this.serviceAccount = new KubeServiceAccount(
      this,
      "licensing-service-account",
      {
        metadata: {
          name,
          namespace,
        },
        imagePullSecrets: imagePullSecrets?.map((secretRef) => ({
          name: secretRef,
        })),
      },
    );
    this.imagePullSecrets = imagePullSecrets;
    const role = new KubeRole(this, "licensing-role", {
      metadata: {
        name,
        namespace,
      },
      rules: [
        {
          apiGroups: [""],
          resources: ["pods"],
          verbs: ["get", "list", "watch"],
        },
      ],
    });

    new KubeRoleBinding(this, "licensing-role-binding", {
      metadata: {
        name,
        namespace,
      },
      roleRef: {
        apiGroup: role.apiGroup,
        kind: role.kind,
        name: role.name,
      },
      subjects: [
        { kind: this.serviceAccount.kind, name: this.serviceAccount.name },
      ],
    });
  }
}
