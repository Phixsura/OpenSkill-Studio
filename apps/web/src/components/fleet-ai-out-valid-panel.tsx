"use client";
export function FleetAiOutValidPanel({ validators, active, validated, rejected, rules }: { validators: number; active: number; validated: number; rejected: number; rules: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ AI Output Validator</h3>
    <div className="text-sm">{active}/{validators} active · {validated.toLocaleString()} validated · {rejected.toLocaleString()} rejected · {rules} rules</div>
  </div>);
}
