"use client";

interface VersionInfo { version: string; type_count: number; query_count: number; mutation_count: number; }
interface RegistryInfo { registry_id: string; service_name: string; current_version: string; version_count: number; latest: VersionInfo | null; }
interface Props { registries: RegistryInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistryCard({ registries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔷 GraphQL Schemas</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {registries.length} registries</p>
      </div>
      {registries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas registered</p>
      ) : (
        <div className="space-y-2">
          {registries.map((r) => (
            <div key={r.registry_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-700 dark:text-gray-300">{r.service_name}</span>
                <span className="rounded bg-purple-100 px-1 text-[9px] text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">{r.current_version}</span>
              </div>
              {r.latest && (
                <div className="mt-0.5 flex gap-2 text-[10px] text-gray-400">
                  <span>{r.latest.type_count} types</span>
                  <span>{r.latest.query_count} queries</span>
                  <span>{r.latest.mutation_count} mutations</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
