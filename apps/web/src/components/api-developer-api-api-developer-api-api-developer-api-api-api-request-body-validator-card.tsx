"use client";

interface Props { stats: { total: number; invalid: number }; ruleCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiRequestBodyValidatorCard({ stats, ruleCount, appName }: Props) {
  const validPct = stats.total > 0 ? Math.round((stats.total - stats.invalid) / stats.total * 100) : 100;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Body Validator</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {ruleCount} rules</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-blue-600">{stats.total}</p>
          <p className="text-[9px] text-gray-400">Validated</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-red-500">{stats.invalid}</p>
          <p className="text-[9px] text-gray-400">Invalid</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className={`text-lg font-bold ${validPct >= 95 ? "text-green-600" : "text-yellow-600"}`}>{validPct}%</p>
          <p className="text-[9px] text-gray-400">Valid Rate</p>
        </div>
      </div>
    </div>
  );
}
