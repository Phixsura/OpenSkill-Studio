"use client";
export function FleetAiSecPosturePanel({ assessors, active, score, vulns, controls, compliance }: { assessors: number; active: number; score: number; vulns: number; controls: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Security Posture</h3>
    <div className="text-sm">{active}/{assessors} active · score {score} · {vulns} vulns · {controls} controls · {compliance}% compliance</div>
  </div>);
}
