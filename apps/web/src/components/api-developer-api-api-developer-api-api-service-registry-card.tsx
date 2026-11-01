"use client";

interface ServiceInfo { service_id: string; name: string; base_url: string; version: string; status: string; tags: string[]; stale: boolean; }
interface Props { services: ServiceInfo[]; staleCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiServiceRegistryCard({ services, staleCount, appName }: Props) {
  const activeCount = services.filter(s => s.status === "active" && !s.stale).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗂️ Service Registry</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {activeCount} active</p>
        </div>
        {staleCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{staleCount} stale</span>}
      </div>
      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No registered services</p>
      ) : (
        <div className="space-y-2">
          {services.map((s) => (
            <div key={s.service_id} className="rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.name}</span>
                <span className="text-[10px] text-gray-400">{s.version}</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {s.tags.map((t) => <span key={t} className="rounded bg-blue-50 px-1 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">{t}</span>)}
                {s.stale && <span className="rounded bg-yellow-100 px-1 py-0.5 text-[9px] text-yellow-700">stale</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
