import { createLicensingApp } from "./lib/licensing/licensing-app";
import { createNamespaceChart } from "./lib/namespace";
import { Segment } from "./lib/types";
import { Namespace } from "./lib/types";
import { App } from "cdk8s";

const SEGMENT = (process.env.SEGMENT as Segment) || Segment.LOC00;
const IMAGE_TAG = process.env.IMAGE_TAG || "";

if (SEGMENT !== Segment.LOC00 && IMAGE_TAG === "") {
  console.error("IMAGE_TAG is '' for remote segment.");
  process.exit(1);
}

const app = new App({ outdir: "dist" });

createNamespaceChart(app, Namespace.LICENSING);

createLicensingApp(app, {
  segment: SEGMENT,
  imageTag: IMAGE_TAG,
  namespace: Namespace.LICENSING,
});

app.synth();
