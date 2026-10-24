"use client";
export function FleetAiChaosMkPanel({ monkeys, active, injections, recovered, unrecovered, recoveryRate }: { monkeys: number; active: number; injections: number; recovered: number; unrecovered: number; recoveryRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐒 AI Chaos Monkey</h3>
    <div className="text-sm">{active}/{monkeys} active · {injections} injections · {recovered} recovered · {recoveryRate}% rate</div>
  </div>);
}
