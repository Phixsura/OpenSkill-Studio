"use client";
export function FleetIngressTlsV9Panel({ ingresses, tls }: { ingresses: number; tls: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Ingress TLS v9</h3>
    <div className="text-sm">{ingresses} ingresses · {tls} TLS</div>
  </div>);
}
