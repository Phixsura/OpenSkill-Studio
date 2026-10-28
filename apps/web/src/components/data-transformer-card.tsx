"use client";

interface TransformRuleInfo {
  rule_id: string;
  rule_type: "rename" | "map_value" | "filter" | "compute" | "default";
  source_field: string;
  target_field: string;
}

interface DataTransformerCardProps {
  rulesetId: string;
  rules: TransformRuleInfo[];
  appName: string;
}

const TYPE_STYLES: Record<string, { icon: string; bg: string; text: string }> = {
  rename: {
    icon: "→",
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-700 dark:text-blue-400",
  },
  map_value: {
    icon: "⇄",
    bg: "bg-purple-100 dark:bg-purple-900/30",
    text: "text-purple-700 dark:text-purple-400",
  },
  filter: {
    icon: "✕",
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
  },
  compute: {
    icon: "ƒ",
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
  },
  default: {
    icon: "=",
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
  },
};

export default function DataTransformerCard({
  rulesetId,
  rules,
  appName,
}: DataTransformerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Transform Rules
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {rulesetId}
          </p>
        </div>
        <span className="text-xs text-gray-400">{rules.length} rules</span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rules defined</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r, i) => {
            const st = TYPE_STYLES[r.rule_type] ?? TYPE_STYLES.default;
            return (
              <div
                key={r.rule_id}
                className="flex items-center gap-2 rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <span className="w-4 text-[11px] text-gray-400">{i + 1}.</span>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${st.bg} ${st.text}`}>
                  {st.icon} {r.rule_type}
                </span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {r.source_field}
                </span>
                {r.target_field && r.target_field !== r.source_field && (
                  <>
                    <span className="text-gray-400">→</span>
                    <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                      {r.target_field}
                    </span>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
