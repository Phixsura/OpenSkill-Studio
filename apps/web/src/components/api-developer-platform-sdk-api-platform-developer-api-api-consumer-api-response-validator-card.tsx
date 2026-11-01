"use client";

interface ExpInfo { endpoint: string; method: string; expected_status: number; field_count: number; }
interface Props { expectations: ExpInfo[]; passRate: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiResponseValidatorCard({ expectations, passRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Response Validator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${passRate >= 95 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{passRate}%</span>
      </div>
      {expectations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No expectations set</p>
      ) : (
        <div className="space-y-1">
          {expectations.map((e) => (
            <div key={`${e.method}-${e.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.method} {e.endpoint}</span>
              <span className="text-gray-400">{e.expected_status} · {e.field_count} fields</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
