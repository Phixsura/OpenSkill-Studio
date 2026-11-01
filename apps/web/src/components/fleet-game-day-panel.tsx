"use client";
export function FleetGameDayPanel({ total, passed, failed, learnings, resilient }: { total: number; passed: number; failed: number; learnings: number; resilient: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎮 Game Day</h3>
    <div className="text-sm">{passed}✅ {failed}❌ · {learnings} learnings</div>
    {!resilient && <span className="text-xs text-yellow-600">⚠️ Weaknesses found</span>}
  </div>);
}
