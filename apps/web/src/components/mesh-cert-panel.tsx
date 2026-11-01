"use client";
interface CertInfo { service: string; fingerprint: string; status: string; validityDays: number; }
interface MeshCertPanelProps { certs: CertInfo[]; active: number; revoked: number; }
export function MeshCertPanel({ certs, active, revoked }: MeshCertPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Mesh Certificates</h3>
        <span className="text-xs text-gray-400">{active} active · {revoked} revoked</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {certs.map(c => (
          <div key={c.service} className="flex justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${c.status === "active" ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{c.service}</span>
            </div>
            <span className="text-gray-400 font-mono text-[10px]">{c.fingerprint} · {c.validityDays}d</span>
          </div>
        ))}
      </div>
    </div>
  );
}
