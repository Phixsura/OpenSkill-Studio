"use client";
export function FleetHealthTlPanel({ snapshots, avgScore, best, worst, trend }: { snapshots: number; avgScore: number; best: number; worst: number; trend: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Health Timeline</h3>
    <div className="text-sm">avg {avgScore} · best {best} · worst {worst} · {trend}</div>
  </div>);
}
