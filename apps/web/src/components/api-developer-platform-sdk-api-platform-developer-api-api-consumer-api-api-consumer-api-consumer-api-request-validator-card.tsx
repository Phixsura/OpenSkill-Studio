"use client";

interface Rule { field: string; type: string; value: string; }
interface Validation { path: string; method: string; rules: Rule[]; }
interface Props { validations: Validation[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidatorCard({ validations, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✔️ Request Validators</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {validations.length} endpoints</p>
      </div>
      {validations.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No validators configured</p>
      ) : (
        <div className="space-y-2">
          {validations.map((v, i) => (
            <div key={i} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center gap-1 text-[11px]">
                <span className="font-bold text-blue-600">{v.method}</span>
                <code className="text-gray-700 dark:text-gray-300">{v.path}</code>
                <span className="text-gray-400">({v.rules.length} rules)</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {v.rules.slice(0, 5).map((r, j) => (
                  <span key={j} className="rounded bg-gray-200 px-1 py-0.5 text-[9px] text-gray-600 dark:bg-gray-700 dark:text-gray-400">{r.field}:{r.type}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
