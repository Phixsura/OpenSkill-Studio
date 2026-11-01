"use client";
export function FleetAiComplianceV8Panel({ frameworks, active, certs, controls, compliance }: { frameworks: number; active: number; certs: string[]; controls: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 AI Compliance v8</h3>
    <div className="text-sm">{active}/{frameworks} active · {certs.join(", ")} · {controls} controls · {compliance}%</div>
  </div>);
}
