"use client";
export function FleetWoodpeckerPanel({ total, success, failed, avgSec }: { total: number; success: number; failed: number; avgSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐦 Woodpecker CI</h3>
    <div className="text-sm">{success}✅ {failed}❌ · avg {avgSec}s</div>
  </div>);
}
