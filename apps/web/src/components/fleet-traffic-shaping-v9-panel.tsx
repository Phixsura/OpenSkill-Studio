"use client";
export function FleetTrafficShapingV9Panel({ rules, rpsLimit }: { rules: number; rpsLimit: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 Traffic Shaping v9</h3>
    <div className="text-sm">{rules} rules · {rpsLimit.toLocaleString()} rps limit</div>
  </div>);
}
