"use client";
export function FleetSslCertMonitorV9Panel({ certs, expiring }: { certs: number; expiring: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 SSL Cert Monitor v9</h3>
    <div className="text-sm">{certs} certs · {expiring} expiring</div>
  </div>);
}
