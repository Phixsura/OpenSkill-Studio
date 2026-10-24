"use client";
export function FleetAiGuardrailV2Panel({ engines, active, evals, blocked, rules }: { engines: number; active: number; evals: number; blocked: number; rules: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Guardrail v2</h3>
    <div className="text-sm">{active}/{engines} active · {evals.toLocaleString()} evals · {blocked.toLocaleString()} blocked · {rules} rules</div>
  </div>);
}
