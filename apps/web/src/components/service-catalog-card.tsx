"use client";

interface ServiceInfo {
  service_id: string;
  name: string;
  owner: string;
  category: string;
  health: "healthy" | "degraded" | "down";
}

interface ServiceCatalogCardProps {
  services: ServiceInfo[];
  appName: string;
}

const HEALTH_DOTS: Record<string, string> = {
  healthy: "bg-green-500",
  degraded: "bg-yellow-500",
  down: "bg-red-500",
};

export default function ServiceCatalogCard({ services, appName }: ServiceCatalogCardProps) {
  const downCount = services.filter((s) => s.health === "down").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Service Catalog
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{services.length} services</span>
          {downCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {downCount} down
            </span>
          )}
        </div>
      </div>

      {services.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No services cataloged</p>
      ) : (
        <div className="space-y-1.5">
          {services.map((s) => (
            <div
              key={s.service_id}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2.5 w-2.5 rounded-full ${HEALTH_DOTS[s.health] ?? HEALTH_DOTS.healthy}`}
                />
                <div>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{s.name}</span>
                  <p className="text-[10px] text-gray-400">
                    {s.owner} · {s.category}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
