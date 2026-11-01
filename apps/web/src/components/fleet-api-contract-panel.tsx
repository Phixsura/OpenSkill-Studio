"use client";
export function FleetApiContractPanel({ total, valid, invalid, allValid }: { total: number; valid: number; invalid: number; allValid: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 API Contracts</h3>
    {allValid ? <span className="text-xs text-green-600">✅ All {total} contracts valid</span>
     : <span className="text-xs text-red-500">⚠️ {invalid} invalid contracts</span>}
  </div>);
}
