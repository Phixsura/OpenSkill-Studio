"use client";
export function FleetZeroTrustV9Panel({ policies, sessions }: { policies: number; sessions: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Zero Trust v9</h3>
    <div className="text-sm">{policies} policies · {sessions} sessions</div>
  </div>);
}
