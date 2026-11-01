"use client";

interface Props { totalRules: number; rejectionRate: number; totalChecked: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddlewareCard({ totalRules, rejectionRate, totalChecked, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Request Validator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRules} rules</p>
        </div>
        <span className={`text-sm font-bold ${rejectionRate < 5 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{rejectionRate}% rejected</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalChecked.toLocaleString()}</div><div className="text-gray-400">Checked</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{totalRules}</div><div className="text-gray-400">Rules</div></div>
      </div>
    </div>
  );
}
