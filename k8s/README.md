# To Get Started

This is giving a brief introduction how to run License-Manager on a local or remote Kubernetes cluster.

## Prerequisites

- nvm: https://github.com/nvm-sh/nvm#installing-and-updating
- npm
- docker
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
  make dist
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
kubectl apply -f dist
```
