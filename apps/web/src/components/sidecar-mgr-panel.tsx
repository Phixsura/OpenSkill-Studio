"use client";

interface SidecarInfo { service: string; proxy: string; mtls: boolean; port: number; }
interface SidecarMgrPanelProps { sidecars: SidecarInfo[]; mtlsEnabled: number; }

export function SidecarMgrPanel({ sidecars, mtlsEnabled }: SidecarMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ Sidecar Proxies</h3>
        <span className="text-xs text-gray-400">{sidecars.length} injected · {mtlsEnabled} mTLS</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {sidecars.map(s => (
          <div key={s.service} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{s.service}</span>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{s.proxy}:{s.port}</span>
              <span className={s.mtls ? "text-green-600" : "text-yellow-600"}>{s.mtls ? "🔒 mTLS" : "⚠ plain"}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
