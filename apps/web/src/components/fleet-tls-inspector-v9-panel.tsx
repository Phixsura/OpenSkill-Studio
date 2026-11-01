"use client";
export function FleetTlsInspectorV9Panel({ endpoints, tls13 }: { endpoints: number; tls13: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 TLS Inspector v9</h3>
    <div className="text-sm">{endpoints} endpoints · {tls13} TLS 1.3</div>
  </div>);
}
