"use client";

interface RuleInfo { rule_id: string; operation: string; source_field: string; }
interface ConfigInfo { consumer_id: string; rules: RuleInfo[]; enabled: boolean; }
interface Props { configs: ConfigInfo[]; totalTransformed: number; appName: string; }

const opIcon: Record<string, string> = { rename: "✏️", remove: "🗑️", add: "➕", mask: "🔒", flatten: "📄", format: "🔄" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseTransformerCard({ configs, totalTransformed, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔧 Response Transformer</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalTransformed.toLocaleString()} transformed</span>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No transform configs</p>
      ) : (
        <div className="space-y-1.5">
          {configs.map((c) => (
            <div key={c.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
                <span className={c.enabled ? "text-green-600 dark:text-green-400" : "text-gray-400"}>{c.enabled ? "on" : "off"}</span>
              </div>
              <div className="flex gap-1 mt-0.5">
                {c.rules.map((r) => <span key={r.rule_id} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{opIcon[r.operation] ?? "•"} {r.source_field}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
