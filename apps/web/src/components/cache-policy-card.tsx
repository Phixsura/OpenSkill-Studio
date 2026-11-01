"use client";

interface CacheRuleInfo {
  rule_id: string;
  path_pattern: string;
  ttl_seconds: number;
  methods: string[];
  enabled: boolean;
  hit_rate: number;
  hits: number;
  misses: number;
}

interface CachePolicyCardProps {
  rules: CacheRuleInfo[];
  appName: string;
}

export default function CachePolicyCard({ rules, appName }: CachePolicyCardProps) {
  const enabled = rules.filter((r) => r.enabled).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⚡ Cache Policy
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {enabled}/{rules.length} enabled
        </span>
      </div>

      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No cache rules</p>
      ) : (
        <div className="space-y-2">
          {rules.map((r) => (
            <div
              key={r.rule_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!r.enabled ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {r.path_pattern}
                </span>
                <span className="text-[11px] text-gray-400">{r.ttl_seconds}s TTL</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                <span>{r.methods.join(", ")}</span>
                <span>
                  {r.hit_rate}% hit rate ({r.hits}h / {r.misses}m)
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
