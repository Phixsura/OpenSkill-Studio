"use client";

interface CapabilityInfo {
  capability_id: string;
  name: string;
  version: string;
  description: string;
}

interface CapabilityRegistryCardProps {
  capabilities: CapabilityInfo[];
  appName: string;
}

export default function CapabilityRegistryCard({
  capabilities,
  appName,
}: CapabilityRegistryCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Capabilities</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{capabilities.length} declared</span>
      </div>

      {capabilities.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No capabilities declared</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {capabilities.map((c) => (
            <div
              key={c.capability_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {c.name}
                </span>
                <span className="rounded bg-blue-100 px-1.5 py-0.5 font-mono text-[10px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                  v{c.version}
                </span>
              </div>
              {c.description && <p className="mt-0.5 text-[11px] text-gray-400">{c.description}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
