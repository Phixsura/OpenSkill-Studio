"use client";

interface RuleInfo { rule_id: string; header_name: string; override: boolean; }
interface ConfigInfo { consumer_id: string; rules: RuleInfo[]; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestHeaderInjectorCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💉 Header Injector</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} configs</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No injection configs</p>
      ) : (
        <div className="space-y-1.5">
          {configs.map((c) => (
            <div key={c.consumer_id} className="text-[11px]">
              <div className="font-medium text-gray-700 dark:text-gray-300">{c.consumer_id}</div>
              <div className="flex gap-1 mt-0.5">
                {c.rules.map((r) => (
                  <span key={r.rule_id} className={`rounded px-1 text-[9px] ${r.override ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>{r.header_name}{r.override ? " ⚠️" : ""}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
