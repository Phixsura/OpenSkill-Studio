"use client";
export function FleetAiModelRbV2Panel({ managers, active, rollbacks, avgTime, successRate }: { managers: number; active: number; rollbacks: number; avgTime: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏪ AI Model Rollback v2</h3>
    <div className="text-sm">{active}/{managers} active · {rollbacks} rollbacks · {avgTime}s avg · {successRate}% success</div>
  </div>);
}
