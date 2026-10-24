"use client";
export function FleetCertManagerV9Panel({ total, expiring }: { total: number; expiring: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Cert Manager v9</h3>
    <div className="text-sm">{total} certs · {expiring} expiring</div>
  </div>);
}
