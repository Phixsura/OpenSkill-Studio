"use client";
export function FleetAiEncryptV8Panel({ systems, active, dataEb, keys, e2e, quantum }: { systems: number; active: number; dataEb: number; keys: number; e2e: boolean; quantum: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Encryption v8</h3>
    <div className="text-sm">{active}/{systems} active · {dataEb}EB · {keys.toLocaleString()} keys · {e2e ? "✅ E2E" : "⚠️"} · {quantum ? "✅ quantum" : "⚠️"}</div>
  </div>);
}
