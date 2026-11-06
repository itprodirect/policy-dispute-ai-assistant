import { Workspace } from "../components/workspace";
import demo from "../data/demo.json";
import sourceMap from "../data/section-text.json";
import type { DemoReport } from "../lib/report";

export default function HomePage() {
  return <Workspace report={demo as DemoReport} sources={sourceMap as Record<string, string>} />;
}
