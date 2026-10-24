"use client";
export function FleetLitmusPanel({ total, passed, failed, resilience, resilient }: { total: number; passed: number; failed: number; resilience: number; resilient: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 LitmusChaos</h3>
    <div className={`text-lg font-bold ${resilient ? "text-green-600" : "text-red-500"}`}>{resilience}% resilient</div>
    <div className="text-xs text-gray-400">{passed}✅ {failed}❌ of {total}</div>
  </div>);
}
