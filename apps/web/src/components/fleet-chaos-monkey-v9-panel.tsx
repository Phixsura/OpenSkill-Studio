"use client";
export function FleetChaosMonkeyV9Panel({ targets, terminated }: { targets: number; terminated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐒 Chaos Monkey v9</h3>
    <div className="text-sm">{targets} targets · {terminated} terminated today</div>
  </div>);
}
