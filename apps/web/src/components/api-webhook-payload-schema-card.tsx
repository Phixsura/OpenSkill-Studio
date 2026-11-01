"use client";

interface SchemaInfo {
  event_type: string;
  required_count: number;
  optional_count: number;
  pass_rate: number;
  validations: number;
}

interface APIWebhookPayloadSchemaCardProps {
  schemas: SchemaInfo[];
  appName: string;
}

export default function APIWebhookPayloadSchemaCard({ schemas, appName }: APIWebhookPayloadSchemaCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📐 Payload Schemas</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{schemas.length} schemas</span>
      </div>

      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No payload schemas</p>
      ) : (
        <div className="space-y-1.5">
          {schemas.map((s) => (
            <div key={s.event_type} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{s.event_type}</span>
                <p className="text-[10px] text-gray-400">{s.required_count} required · {s.optional_count} optional</p>
              </div>
              <span className={`text-[11px] font-medium ${s.pass_rate >= 95 ? "text-green-600" : "text-red-500"}`}>{s.pass_rate}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
