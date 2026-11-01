"use client";
export function FleetCfgValidatePanel({ total, valid, invalid, safeToDeploy }: { total: number; valid: number; invalid: number; safeToDeploy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Config Validation</h3>
    {safeToDeploy ? <span className="text-xs text-green-600">✅ All {total} configs valid</span>
     : <span className="text-xs text-red-500">❌ {invalid} invalid configs — deploy blocked</span>}
  </div>);
}
