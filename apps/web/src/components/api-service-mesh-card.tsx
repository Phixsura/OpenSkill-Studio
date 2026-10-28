"use client";

interface MeshServiceInfo {
  service_id: string;
  name: string;
  call_count: number;
  error_rate: number;
}

interface LinkInfo {
  source: string;
  target: string;
  call_count: number;
}

interface APIServiceMeshCardProps {
  services: MeshServiceInfo[];
  links: LinkInfo[];
  appName: string;
}

export default function APIServiceMeshCard({ services, links, appName }: APIServiceMeshCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🕸️ Service Mesh</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{services.length} services · {links.length} links</span>
      </div>

      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No services in mesh</p>
      ) : (
        <>
          <div className="mb-2 space-y-1">
            {services.map((s) => (
              <div key={s.service_id} className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{s.name}</span>
                <span className={`text-gray-400 ${s.error_rate > 5 ? "text-red-500" : ""}`}>{s.call_count} calls · {s.error_rate}% err</span>
              </div>
            ))}
          </div>
          {links.length > 0 && (
            <div className="border-t border-gray-100 pt-2 dark:border-gray-800">
              {links.slice(0, 5).map((l, i) => (
                <p key={i} className="text-[10px] text-gray-400">{l.source} → {l.target} ({l.call_count})</p>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
