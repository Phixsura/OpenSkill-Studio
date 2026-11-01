"use client";

interface SchemaInfo { endpoint: string; method: string; required_count: number; typed_count: number; }
interface Props { schemas: SchemaInfo[]; validationRate: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestBodyValidatorCard({ schemas, validationRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Body Validator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schemas.length} schemas</p>
        </div>
        <span className={`text-sm font-bold ${validationRate >= 95 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{validationRate}%</span>
      </div>
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No body schemas</p>
      ) : (
        <div className="space-y-1">
          {schemas.map((s) => (
            <div key={`${s.method}-${s.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.method} {s.endpoint}</span>
              <span className="text-gray-400">{s.required_count} req · {s.typed_count} typed</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
