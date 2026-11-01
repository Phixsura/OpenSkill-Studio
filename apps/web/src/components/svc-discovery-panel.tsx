"use client";

interface DiscoveredService { name: string; endpoint: string; tags: string[]; }
interface SvcDiscoveryPanelProps { services: DiscoveredService[]; healthy: number; stale: number; }

export function SvcDiscoveryPanel({ services, healthy, stale }: SvcDiscoveryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Service Discovery</h3>
        <span className="text-xs text-gray-400">{healthy} healthy · {stale} stale</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-semibold">{s.name}</span>
              <span className="text-gray-400 font-mono ml-2">{s.endpoint}</span>
            </div>
            <div className="flex gap-1">
              {s.tags.map(t => (
                <span key={t} className="px-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px]">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
