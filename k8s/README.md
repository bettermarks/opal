# To Get Started

This is giving a brief introduction how to run License-Manager on a local or remote Kubernetes cluster.

## Prerequisites

- nvm: https://github.com/nvm-sh/nvm#installing-and-updating
- npm
- docker
- skaffold: https://skaffold.dev/docs/install/
- kubectl: https://kubernetes.io/docs/tasks/tools/#kubectl
- Locally running Kubernetes Cluster from any of the below options
  - Docker Desktop: https://www.docker.com/products/docker-desktop/
  - kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation
  - minikube: https://minikube.sigs.k8s.io/docs/start/
- Helm: https://helm.sh/docs/intro/install/
- cdk8s
  - On MAC:
    ```sh
    brew install cdk8s
    ```
  - On Linux:
    ```sh
    npm install -g cdk8s-cli
    ```

## How to use the npm commands

### Compile

- Compile typescript code to javascript:
  ```sh
  npm run compile
  ```
  or
  ```sh
  yarn watch
  ```
- Watch for changes and compile typescript in the background:
  ```
  npm run watch
  ```
- Compile and synthesize:
  ```sh
  npm run build
  ```

#### Synthesize

- Synthesize k8s manifests from charts to dist/ (ready for 'kubectl apply -f')
  ```sh
  make k8s_synth
  ```

### Upgrades

- Import/update k8s apis (you should check-in this directory):
  ```sh
  npm run import
  ```
- Upgrade cdk8s modules to latest version:
  ```sh
  npm run upgrade
  ```
- Upgrade cdk8s modules to latest "@next" version (last commit)
  ```sh
  npm run upgrade:next
  ```

## Deploy K8s manifests

```sh
kubectl apply -f dist/<segment>-*yaml
```

## Set up License-Service locally

1. Switch to `k8s` folder:
   ```sh
   cd k8s
   ```
2. Ensure using the right version of Node configured in `.nvmrc`:
   ```sh
   nvm use
   ```
3. Install the required packages listed the `package.json`:
   ```sh
   npm install
   ```
4. Run snapshot tests and synthesize the K8s manifests from charts to `dist/` folder:
   ```sh
   npm run build
   ```
5. Apply the K8S manifests to the local Kubernetes cluster with the help of `skaffold` and `kustomize` and wait until the `licensing-deployment-**\*** pod` is running:
   ```sh
   cd ..
   skaffold dev
   ```
   All required credentials for local development are part of the repo in `k8s/loc00` folder.
6. In oder to access the environment locally you need to add the following line to the `/etc/hosts` file:
   ```sh
   echo "127.0.0.1 licensing.opal.loc" | sudo tee -a >> /etc/hosts
   ```
7. License-Service status:
   https://licensing.opal.loc:8443/v1/status

### Connect to local postgres (licensing-db)

To be able to connect to the licensing-db service you need to forward the port (configured to :5433):

```sh
   make pg-port-forward
```

This is also helpful for running tests.

## Set up License-Service on remote cluster

#### Prerequisites

- The target cluster must exist.
- The target cluster should have been configured with required secrets and tools as described in [README.md](https://github.com/bettermarks/bm-operations/blob/master/cdk8s/README.md)
  - Required secrets:
    - licensing-postgres-secret
    - licensing-application-secret
    - registry-credentials
  - Required deployments:
    - Postgres DB cluster
    - Cloudflare tunnel
- You need a `kubeconfig` file to access the target cluster.

1. Switch to `ks8` folder:
   ```sh
   cd k8s
   ```
2. Ensure using the right version of Node configured in `.nvmrc`:
   ```sh
   nvm use
   ```
3. Install the required packages listed in `package.json`:
   ```sh
   npm install
   ```
4. Create K8s manifests from charts to `dist/` folder for the target segment:
   ```sh
   SEGMENT=<segment> IMAGE_TAG=<image_tag> npm run synth
   ```
5. Connect ot the remote cluster:
   ```
   export KUBECONFIG=</path/to/kubeconfig>
   ```
6. Deploy the K8s manifests:
   ```
   kubectl apply -f dist/<segment>-*yaml
   ```

## Other useful kubectl commands to see the created resources

1. In order to see the pods created under the namespace `licensing`:
   ```sh
   kubectl -n licensing get pods
   ```
2. In order to see the secrets created under the namespace `licensing`:
   ```sh
   kubectl -n licensing get secrets
   ```
3. In order to see the cronjobs created under the namespace `licensing`:
   ```sh
   kubectl -n licensing get cronjobs
   ```
4. In order to see the jobs created under the namespace `licensing`:
   ```sh
   kubectl -n licensing get jobs
   ```
5. In order to see the configmaps created under the namespace `licensing`:
   ```sh
   kubectl -n licensing get configmap
   ```
6. In order to see the deployments created under the namespace `licensing`:
   ```sh
   kubectl -n licensing get deployments
   ```
7. In order to see the cronjobs created under the namespace `licensing`:
   ```sh
   kubectl -n licensing logs <podname>
   ```
8. In order to describe the specific details of the resource created under the namespace `licensing`:
   ```sh
   kubectl -n licensing describe <resource_type> <resource_name>
   ```
9. In order to create/configure the resource created:
   ```sh
   kubectl -n licensing apply <folder_name>/<specific.yaml>
   ```
10. In order to debug a container of a pod via pdb (this picks the first available container in the pod)

````sh
kubectl -n licensing get pods
kubectl -n licensing attach POD_NAME -it


## Structure

```mermaid
classDiagram

class PostgresChart {
+ConfigMap configMap
+Secret secret
+KubeService kubeService
+KubeDeployment kubeDeployment
}

class LicensingChart {
+KubeServiceAccount serviceAccount
+KubeRole role
+KubeRoleBinding
+LicensingService licensingService
+KubeIngress
}

class IngressNginxChart {
+Helm ingressNginx
}

class LicensingService {
+KubeDeployment
+KubeService
}

App --> PostgresChart
App --> LicensingChart
App --> IngressNginxChart
LicensingChart --> LicensingService

````
