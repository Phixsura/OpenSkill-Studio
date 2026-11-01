"use client";

interface ThrottleRuleInfo {
  rule_id: string;
  path_pattern: string;
  max_requests: number;
  window_seconds: number;
  enabled: boolean;
}

interface APIThrottleRuleCardProps {
  rules: ThrottleRuleInfo[];
  appName: string;
}

export default function APIThrottleRuleCard({ rules, appName }: APIThrottleRuleCardProps) {
  const enabled = rules.filter((r) => r.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Throttle Rules</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{enabled}/{rules.length} active</span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No throttle rules</p>
      ) : (
        <div className="space-y-1.5">
          {rules.map((r) => (
            <div key={r.rule_id} className={`flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${!r.enabled ? "opacity-50" : ""}`}>
              <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{r.path_pattern}</span>
              <span className="text-[10px] text-gray-400">{r.max_requests}/{r.window_seconds}s</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
