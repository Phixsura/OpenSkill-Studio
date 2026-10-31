"use client";

interface RuleInfo { endpoint: string; method: string; allowed_roles: string[]; public: boolean; }
interface Props { rules: RuleInfo[]; appName: string; }

export default function APIDeveloperAPIApiAccessControlMatrixCard({ rules, appName }: Props) {
  const publicCount = rules.filter(r => r.public).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ Access Control Matrix</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
        </div>
        <span className="text-[10px] text-gray-400">{publicCount} public</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No access rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-500">{r.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.endpoint}</span>
              </div>
              {r.public ? (
                <span className="rounded bg-green-100 px-1 py-0.5 text-[9px] text-green-700">public</span>
              ) : (
                <span className="text-[10px] text-gray-400">{r.allowed_roles.join(", ")}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
