"use client";

interface NetworkRuleInfo {
  rule_id: string;
  direction: "egress" | "ingress";
  action: "allow" | "deny";
  destination: string;
  port: number | null;
  protocol: string;
}

interface NetworkPolicyCardProps {
  rules: NetworkRuleInfo[];
  appName: string;
}

export default function NetworkPolicyCard({ rules, appName }: NetworkPolicyCardProps) {
  const denyCount = rules.filter((r) => r.action === "deny").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Network Policy</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{rules.length} rules</span>
          {denyCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {denyCount} deny
            </span>
          )}
        </div>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No network rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div
              key={r.rule_id}
              className="flex items-center justify-between rounded px-2.5 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs font-bold ${r.action === "allow" ? "text-green-600" : "text-red-500"}`}
                >
                  {r.action === "allow" ? "✓" : "✕"}
                </span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">
                  {r.direction}
                </span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {r.destination}
                </span>
              </div>
              <span className="text-[11px] text-gray-400">
                {r.port ? `port ${r.port}` : "any port"} · {r.protocol}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
