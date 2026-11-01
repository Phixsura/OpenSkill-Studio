"use client";
export function FleetAiEncryptV4Panel({ systems, active, data, keys, rotations, e2e }: { systems: number; active: number; data: number; keys: number; rotations: number; e2e: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Encryption v4</h3>
    <div className="text-sm">{active}/{systems} active · {data}TB encrypted · {keys.toLocaleString()} keys · {rotations} rotations · {e2e ? "✅ E2E" : "⚠️"}</div>
  </div>);
}
