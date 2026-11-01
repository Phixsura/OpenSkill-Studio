"use client";
export function FleetAiReqValidPanel({ validators, active, validated, rejected, schemas }: { validators: number; active: number; validated: number; rejected: number; schemas: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ AI Request Validator</h3>
    <div className="text-sm">{active}/{validators} active · {validated.toLocaleString()} validated · {rejected.toLocaleString()} rejected · {schemas} schemas</div>
  </div>);
}
