"use client";

interface Stats { valid: number; invalid: number; validation_rate: number; }
interface Props { stats: Stats; maxPayloadKb: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidatorCard({ stats, maxPayloadKb, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Payload Validator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — max {maxPayloadKb} KB</p>
        </div>
        <span className={`text-sm font-bold ${stats.validation_rate >= 95 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{stats.validation_rate}%</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-green-600 dark:text-green-400">{stats.valid.toLocaleString()}</div><div className="text-gray-400">Valid</div></div>
        <div><div className="font-semibold text-red-600 dark:text-red-400">{stats.invalid}</div><div className="text-gray-400">Invalid</div></div>
      </div>
    </div>
  );
}
