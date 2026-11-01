"use client";
export function FleetSessionStoreV9Panel({ active, expired }: { active: number; expired: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎫 Session Store v9</h3>
    <div className="text-sm">{active} active · {expired} expired</div>
  </div>);
}
