"use client";
export function FleetImgAgePanel({ total, old, ancient, fresh, needsUpdate }: { total: number; old: number; ancient: number; fresh: number; needsUpdate: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Image Age</h3>
    <div className="text-sm">{fresh} fresh · {old} old · {ancient} ancient</div>
    {needsUpdate && <span className="text-xs text-yellow-600">⚠️ {ancient} images {">"} 90 days old</span>}
  </div>);
}
