"use client";
export function FleetDarkLaunchPanel({ total, darkLaunching, avgShadowPct }: { total: number; darkLaunching: number; avgShadowPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌑 Dark Launch</h3>
    <div className="text-sm">{darkLaunching}/{total} features · avg {avgShadowPct}% shadow</div>
  </div>);
}
