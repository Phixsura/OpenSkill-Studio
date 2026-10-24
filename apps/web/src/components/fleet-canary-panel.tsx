"use client";
export function FleetCanaryPanel({ activeCanaries, promoted, failed, total }: { activeCanaries: number; promoted: number; failed: number; total: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐦 Canary Deploys</h3>
    <div className="text-sm">🟡 {activeCanaries} active · ✅ {promoted} promoted · ❌ {failed} failed</div>
  </div>);
}
