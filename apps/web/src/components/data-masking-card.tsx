"use client";

interface MaskRuleInfo {
  field: string;
  strategy: "full" | "partial" | "hash" | "redact";
  visible_chars: number;
}

interface DataMaskingCardProps {
  rulesetId: string;
  rules: MaskRuleInfo[];
  appName: string;
}

const STRATEGY_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  full: {
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    label: "Full mask",
  },
  partial: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
    label: "Partial",
  },
  hash: {
    bg: "bg-blue-100 dark:bg-blue-900/30",
    text: "text-blue-700 dark:text-blue-400",
    label: "Hash",
  },
  redact: {
    bg: "bg-purple-100 dark:bg-purple-900/30",
    text: "text-purple-700 dark:text-purple-400",
    label: "Redact",
  },
};

export default function DataMaskingCard({ rulesetId, rules, appName }: DataMaskingCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Data Masking</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {rulesetId}
          </p>
        </div>
        <span className="text-xs text-gray-400">{rules.length} rules</span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No masking rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => {
            const st = STRATEGY_STYLES[r.strategy] ?? STRATEGY_STYLES.full;
            return (
              <div
                key={r.field}
                className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                    {r.field}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${st.bg} ${st.text}`}
                  >
                    {st.label}
                  </span>
                </div>
                {r.strategy === "partial" && (
                  <span className="text-[10px] text-gray-400">show {r.visible_chars} chars</span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
