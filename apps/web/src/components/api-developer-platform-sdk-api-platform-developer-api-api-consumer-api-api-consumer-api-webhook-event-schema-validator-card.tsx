"use client";

interface Field { name: string; type: string; required: boolean; }
interface Schema { id: string; eventType: string; version: string; fields: Field[]; }
interface Props { schemas: Schema[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidatorCard({ schemas, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Event Schemas</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schemas.length} schemas</p>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas registered</p>
      ) : (
        <div className="space-y-2">
          {schemas.map((s) => (
            <div key={s.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{s.eventType}</span>
                <span className="text-[10px] text-gray-400">v{s.version}</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {s.fields.map((f) => (
                  <span key={f.name} className={`rounded px-1 py-0.5 text-[9px] ${f.required ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" : "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400"}`}>
                    {f.name}: {f.type}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
