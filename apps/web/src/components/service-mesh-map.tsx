"use client";

interface ServiceNode { serviceId: string; extensionId: string; url: string; circuitOpen: boolean; requestCount: number; errorCount: number; }

export function ServiceMeshMap({ services }: { services: ServiceNode[] }) {
  const healthy = services.filter(s => !s.circuitOpen).length;
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-sm">Service Mesh</h3>
        <span className="text-xs text-gray-500">{healthy}/{services.length} healthy</span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {services.map(s => (
          <div key={s.serviceId} className={`border rounded-xl p-3 text-center ${
            s.circuitOpen ? "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-900/10" : "border-green-200 dark:border-gray-700"
          }`}>
            <span className={`text-xl block ${s.circuitOpen ? "text-red-500" : "text-green-500"}`}>
              {s.circuitOpen ? "🔴" : "🟢"}
            </span>
            <span className="font-medium text-sm block">{s.serviceId}</span>
            <span className="text-[10px] text-gray-500">{s.requestCount} req · {s.errorCount} err</span>
            {s.circuitOpen && <span className="text-[10px] text-red-500 block">CIRCUIT OPEN</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
