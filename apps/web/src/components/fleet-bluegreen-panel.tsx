"use client";
export function FleetBluegreenPanel({ total, greenLive, blueLive, switching, stable }: { total: number; greenLive: number; blueLive: number; switching: number; stable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔵🟢 Blue-Green</h3>
    <div className="text-sm">🟢 {greenLive} live · 🔵 {blueLive} standby</div>
    {!stable && <span className="text-xs text-yellow-600">🔄 {switching} switching</span>}
  </div>);
}
