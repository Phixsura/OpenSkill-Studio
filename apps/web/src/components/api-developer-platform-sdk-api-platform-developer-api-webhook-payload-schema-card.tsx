"use client";

interface SchemaInfo { schema_id: string; event_type: string; version: string; field_count: number; required_count: number; }
interface Props { schemas: SchemaInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchemaCard({ schemas, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Payload Schemas</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schemas.length} schemas</p>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas registered</p>
      ) : (
        <div className="space-y-1.5">
          {schemas.map((s) => (
            <div key={s.schema_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-700 dark:text-gray-300">{s.event_type}</span>
                <span className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">v{s.version}</span>
              </div>
              <span className="text-gray-400">{s.required_count}/{s.field_count} required</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
