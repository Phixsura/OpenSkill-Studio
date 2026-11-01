"use client";

interface SchemaInfo { event_type: string; version: string; field_count: number; required_count: number; description: string; }
interface Props { schemas: SchemaInfo[]; eventTypes: string[]; appName: string; }

export default function APIDeveloperAPIWebhookEventSchemaRegistryCard({ schemas, eventTypes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Event Schema Registry</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {eventTypes.length} event types</p>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas registered</p>
      ) : (
        <div className="space-y-2">
          {schemas.map((s) => (
            <div key={`${s.event_type}-${s.version}`} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.event_type}</span>
                <span className="rounded bg-green-100 px-1.5 py-0.5 text-[9px] text-green-700">v{s.version}</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">{s.field_count} fields · {s.required_count} required</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
