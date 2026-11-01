"use client";
export function FleetTokenRotationV9Panel({ total, expired }: { total: number; expired: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 Token Rotation v9</h3>
    <div className="text-sm">{total} tokens · {expired} expired</div>
  </div>);
}
