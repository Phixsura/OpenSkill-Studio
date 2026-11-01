"use client";
export function FleetAiDataValidPanel({ validators, active, validated, issues, rules }: { validators: number; active: number; validated: number; issues: number; rules: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ AI Data Validator</h3>
    <div className="text-sm">{active}/{validators} active · {validated.toLocaleString()} validated · {issues.toLocaleString()} issues · {rules} rules</div>
  </div>);
}
