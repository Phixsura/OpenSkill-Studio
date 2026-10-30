"use client";

interface Field { name: string; value: string; type: string; }
interface Props { fields: Field[]; consumerId: string; maxFields: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerCustomFieldCard({ fields, consumerId, maxFields, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ Custom Fields</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {fields.length}/{maxFields} fields</p>
      </div>
      {fields.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom fields</p>
      ) : (
        <div className="space-y-1">
          {fields.map((f) => (
            <div key={f.name} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <div className="flex items-center gap-1">
                <code className="font-medium text-gray-700 dark:text-gray-300">{f.name}</code>
                <span className="rounded bg-gray-200 px-1 py-0.5 text-[8px] text-gray-500 dark:bg-gray-700">{f.type}</span>
              </div>
              <span className="max-w-[50%] truncate text-gray-500">{f.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
