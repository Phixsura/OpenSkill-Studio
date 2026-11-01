"use client";

interface ValidationInfo { destination: string; total_validated: number; valid_rate: number; invalid_count: number; last_error: string; }
interface Props { validations: ValidationInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiWebhookPayloadValidatorCard({ validations, appName }: Props) {
  const totalInvalid = validations.reduce((s, v) => s + v.invalid_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Payload Validator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {totalInvalid > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{totalInvalid} invalid</span>}
      </div>
      {validations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No validations</p>
      ) : (
        <div className="space-y-1.5">
          {validations.map((v) => (
            <div key={v.destination} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{new URL(v.destination).hostname}</span>
              <span className={v.valid_rate >= 99 ? "text-green-600" : "text-red-500"}>{v.valid_rate}% valid · {v.total_validated} checked</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
