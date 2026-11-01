"use client";

interface Rule { field: string; type: string; value: string; }
interface Schema { id: string; endpoint: string; method: string; rules: Rule[]; }
interface Props { schemas: Schema[]; appName: string; }

const ruleColors: Record<string, string> = {
  required: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  type: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  pattern: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  range: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  min_length: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  max_length: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
};

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2Card({ schemas, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✔️ Request Validator V2</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schemas.length} schemas</p>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No validation schemas</p>
      ) : (
        <div className="space-y-2">
          {schemas.map((s) => (
            <div key={s.id} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center gap-1 text-[11px]">
                <span className="font-bold text-blue-600">{s.method}</span>
                <code className="text-gray-700 dark:text-gray-300">{s.endpoint}</code>
                <span className="text-gray-400">({s.rules.length} rules)</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {s.rules.slice(0, 5).map((r, i) => (
                  <span key={i} className={`rounded px-1 py-0.5 text-[8px] ${ruleColors[r.type] ?? "bg-gray-200 text-gray-600"}`}>{r.field}:{r.type}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
