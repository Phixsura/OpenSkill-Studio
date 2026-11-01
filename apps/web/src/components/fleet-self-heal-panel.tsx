"use client";
export function FleetSelfHealPanel({ total, autoRecovered, manual, automationRate, mature }: { total: number; autoRecovered: number; manual: number; automationRate: number; mature: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Self-Healing</h3>
    <div className={`text-lg font-bold ${mature ? "text-green-600" : "text-yellow-600"}`}>{automationRate}% auto</div>
    <div className="text-xs text-gray-400">{autoRecovered} auto · {manual} manual</div>
  </div>);
}
