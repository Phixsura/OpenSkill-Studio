"use client";

interface SchemaInfo { event_type: string; version: string; field_count: number; deprecated: boolean; }
interface Props { schemas: SchemaInfo[]; appName: string; }

export default function APIWebhookEventSchemaRegistryCard({ schemas, appName }: Props) {
  const deprecated = schemas.filter((s) => s.deprecated).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Schema Registry</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{schemas.length} schemas</span>
          {deprecated > 0 && <p className="text-[10px] text-yellow-600">{deprecated} deprecated</p>}
        </div>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas registered</p>
      ) : (
        <div className="space-y-1">
          {schemas.map((s) => (
            <div key={`${s.event_type}-${s.version}`} className={`flex items-center justify-between text-[11px] ${s.deprecated ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span className="text-gray-700 dark:text-gray-300">{s.event_type}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">v{s.version}</span>
              </div>
              <span className="text-gray-400">{s.field_count} fields</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
