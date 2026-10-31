"use client";

interface Version { version: string; fieldCount: number; deprecatedCount: number; changelog: string; }
interface Compat { from: string; to: string; added: string[]; removed: string[]; breaking: boolean; }
interface Props { versions: Version[]; compat: Compat | null; endpointPath: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchemaCard({ versions, compat, endpointPath, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Versioned Schema</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — <code>{endpointPath}</code></p>
      </div>
      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schema versions</p>
      ) : (
        <div className="mb-3 space-y-1">
          {versions.map((v) => (
            <div key={v.version} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <span className="font-bold text-blue-600 dark:text-blue-400">{v.version}</span>
              <span className="text-gray-400">{v.fieldCount} fields{v.deprecatedCount > 0 && ` · ${v.deprecatedCount} deprecated`}</span>
            </div>
          ))}
        </div>
      )}
      {compat && (
        <div className={`rounded-lg p-2 text-[10px] ${compat.breaking ? "bg-red-50 dark:bg-red-900/20" : "bg-green-50 dark:bg-green-900/20"}`}>
          <div className="font-medium">{compat.from} → {compat.to}: {compat.breaking ? "⚠️ Breaking" : "✅ Compatible"}</div>
          {compat.added.length > 0 && <div className="text-green-600">+{compat.added.join(", ")}</div>}
          {compat.removed.length > 0 && <div className="text-red-600">-{compat.removed.join(", ")}</div>}
        </div>
      )}
    </div>
  );
}
