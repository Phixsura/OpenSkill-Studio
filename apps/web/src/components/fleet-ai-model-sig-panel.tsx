"use client";
export function FleetAiModelSigPanel({ validators, active, models, schemas, violations }: { validators: number; active: number; models: number; schemas: number; violations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✍️ AI Model Signature</h3>
    <div className="text-sm">{active}/{validators} active · {models} models · {schemas} schemas · {violations} violations</div>
  </div>);
}
