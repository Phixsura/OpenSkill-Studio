"use client";
export function FleetAiPlatSecretV3Panel({ managers, active, secrets, rotations, encrypted }: { managers: number; active: number; secrets: number; rotations: number; encrypted: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Secrets v3</h3>
    <div className="text-sm">{active}/{managers} active · {secrets.toLocaleString()} secrets · {rotations} rotations · {encrypted ? "✅" : "⚠️"} encrypted</div>
  </div>);
}
