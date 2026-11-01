"use client";
export function FleetAiModelGovV7Panel({ systems, active, models, approved, rejected, compliance }: { systems: number; active: number; models: number; approved: number; rejected: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚖️ AI Model Gov v7</h3>
    <div className="text-sm">{active}/{systems} active · {models} models · ✅{approved} · ❌{rejected} · {compliance}%</div>
  </div>);
}
