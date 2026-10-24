"use client";
export function FleetChaosMonkeyPanel({ enabled, terminated, survived, survivalRate }: { enabled: boolean; terminated: number; survived: number; survivalRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐒 Chaos Monkey</h3>
    <div className="text-sm">{enabled ? "🟢 Active" : "🔴 Disabled"} · {terminated} terminated · {survivalRate}% survived</div>
  </div>);
}
