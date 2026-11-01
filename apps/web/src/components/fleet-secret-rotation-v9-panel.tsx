"use client";
export function FleetSecretRotationV9Panel({ total, rate }: { total: number; rate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 Secret Rotation v9</h3>
    <div className="text-sm">{total} secrets · {rate}% rotated</div>
  </div>);
}
