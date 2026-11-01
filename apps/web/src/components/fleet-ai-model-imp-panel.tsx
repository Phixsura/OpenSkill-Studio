"use client";
export function FleetAiModelImpPanel({ importers, active, imports, validated, rejected }: { importers: number; active: number; imports: number; validated: number; rejected: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📥 AI Model Import</h3>
    <div className="text-sm">{active}/{importers} active · {imports.toLocaleString()} imports · ✅{validated} · ❌{rejected}</div>
  </div>);
}
