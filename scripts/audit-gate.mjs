#!/usr/bin/env node
// R557: dependency-audit CI gate. `pnpm audit` has no ignore list, so this
// wraps it: fail on ANY advisory not explicitly dispositioned below.
import { execSync } from "node:child_process";

// GHSA id -> why it is accepted. Revisit on every entry.
const DISPOSITIONED = {
  // braces ReDoS: no patched version exists upstream (patched: <0.0.0);
  // reachable only through eslint-config dev tooling, never at runtime.
  "GHSA-vfj7-8cjw-p6xm": "braces ReDoS - no upstream patch; dev-tooling path",
};

let out = "";
try {
  out = execSync(
    "pnpm audit --prod --json --registry=https://registry.npmjs.org",
    { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] },
  );
} catch (err) {
  // pnpm audit exits non-zero when advisories exist; the JSON is still on stdout.
  out = err.stdout?.toString() ?? "";
  if (!out) {
    console.error("audit-gate: pnpm audit produced no output", err.stderr?.toString());
    process.exit(2);
  }
}

const report = JSON.parse(out);
const advisories = Object.values(report.advisories ?? {});
let blocking = 0;
for (const a of advisories) {
  const ghsa = a.github_advisory_id;
  if (DISPOSITIONED[ghsa]) {
    console.log(`allowed  ${ghsa} ${a.module_name}: ${DISPOSITIONED[ghsa]}`);
  } else {
    blocking += 1;
    console.error(`BLOCKING ${ghsa} ${a.module_name} (${a.severity}): ${a.title}`);
  }
}
console.log(`audit-gate: ${advisories.length} advisories, ${blocking} blocking`);
process.exit(blocking ? 1 : 0);
