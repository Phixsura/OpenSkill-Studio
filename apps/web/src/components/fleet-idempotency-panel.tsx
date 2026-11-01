"use client";
export function FleetIdempotencyPanel({ total, withIdemp, replayed, coveragePct }: { total: number; withIdemp: number; replayed: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔁 Idempotency</h3>
    <div className="text-sm">{withIdemp}/{total} endpoints ({coveragePct}%) · {replayed} replays</div>
  </div>);
}
