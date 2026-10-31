"use client";

interface MirrorRuleInfo {
  rule_id: string;
  source_path: string;
  shadow_target: string;
  sample_rate: number;
  enabled: boolean;
  mirrored_count: number;
  divergence_rate: number;
}

interface TrafficMirrorCardProps {
  rules: MirrorRuleInfo[];
  appName: string;
}

function formatNum(n: number): string {
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function TrafficMirrorCard({ rules, appName }: TrafficMirrorCardProps) {
  const activeCount = rules.filter((r) => r.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Traffic Mirror</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {activeCount}/{rules.length} active
        </span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No mirror rules</p>
      ) : (
        <div className="space-y-2">
          {rules.map((r) => (
            <div
              key={r.rule_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!r.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2 w-2 rounded-full ${r.enabled ? "bg-green-500" : "bg-gray-300"}`}
                  />
                  <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                    {r.source_path}
                  </span>
                  <span className="text-gray-400">→</span>
                  <span className="max-w-[150px] truncate font-mono text-xs text-blue-600 dark:text-blue-400">
                    {r.shadow_target}
                  </span>
                </div>
                <span className="text-[10px] text-gray-400">
                  {(r.sample_rate * 100).toFixed(0)}%
                </span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[11px] text-gray-400">
                <span>{formatNum(r.mirrored_count)} mirrored</span>
                <span className={r.divergence_rate > 5 ? "text-red-500" : "text-gray-400"}>
                  {r.divergence_rate.toFixed(1)}% divergence
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
