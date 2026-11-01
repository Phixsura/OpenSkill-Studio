"use client";

interface Service { name: string; address: string; tags: string[]; status: string; }
interface SvcDiscoveryBrowserProps { services: Service[]; total: number;
  healthy: number; tags: string[]; onDeregister: (name: string) => void; }

export function SvcDiscoveryBrowser({ services, total, healthy, tags, onDeregister }: SvcDiscoveryBrowserProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Service Discovery</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{healthy}/{total} healthy</span>
          <span className="text-gray-400">{tags.length} tags</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${s.status === "healthy" ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-sm font-medium">{s.name}</span>
                <span className="text-xs font-mono text-gray-400">{s.address}</span>
              </div>
              <div className="flex gap-1 mt-0.5">
                {s.tags.map(t => (
                  <span key={t} className="px-1 py-0.5 text-[10px] bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded">{t}</span>
                ))}
              </div>
            </div>
            <button onClick={() => onDeregister(s.name)} className="text-xs text-red-500 hover:underline">Remove</button>
          </div>
        ))}
      </div>
    </div>
  );
}
