import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import assert from "node:assert/strict";

const repoRoot = resolve(import.meta.dirname, "../..");
const webRoot = resolve(import.meta.dirname, "..");
for (const [source, copy] of [
  ["assets/demo/demo.json", "data/demo.json"],
  ["assets/demo/section_text.json", "data/section-text.json"],
  ["assets/demo/demo.report.md", "public/demo-report.md"],
]) {
  const original = readFileSync(resolve(repoRoot, source), "utf8").trim();
  const local = readFileSync(resolve(webRoot, copy), "utf8").trim();
  assert.equal(local, original, "Demo asset must exactly match original: " + copy);
}

const report = JSON.parse(readFileSync(resolve(webRoot, "data/demo.json"), "utf8"));
const sourceMap = JSON.parse(readFileSync(resolve(webRoot, "data/section-text.json"), "utf8"));
assert.equal(Object.keys(sourceMap).length, 13, "Expected the 13 existing synthetic source excerpts.");
for (const key of ["plain_summary", "coverage_highlights", "exclusions_limitations", "denial_reasons", "dispute_angles", "missing_info", "confidence"]) {
  assert.ok(report[key] != null, "Missing A–G field: " + key);
}
console.log("Demo parity passed: A–G report, Markdown, and 13 source excerpts match originals.");
