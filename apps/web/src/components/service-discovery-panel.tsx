"use client";

interface Instance { instance_id: string; service_name: string; address: string; status: string; tags: string[]; }
interface ServiceDiscoveryPanelProps { services: { name: string; instances: Instance[] }[]; }

export function ServiceDiscoveryPanel({ services }: ServiceDiscoveryPanelProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Service Registry</h2>
      {services.map(svc => {
        const healthy = svc.instances.filter(i => i.status === "healthy").length;
        return (
          <div key={svc.name} className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="font-medium">{svc.name}</span>
              <span className="text-xs text-gray-400">{healthy}/{svc.instances.length} healthy</span>
            </div>
            <div className="mt-2 space-y-1">
              {svc.instances.map(i => (
                <div key={i.instance_id} className="flex items-center gap-2 text-xs">
                  <span className={`h-2 w-2 rounded-full ${i.status === "healthy" ? "bg-green-500" : "bg-red-500"}`} />
                  <span className="font-mono">{i.address}</span>
                  {i.tags.map(t => <span key={t} className="rounded bg-gray-100 px-1 py-0.5 dark:bg-gray-800">{t}</span>)}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
