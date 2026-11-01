"use client";

interface OverrideInfo {
  override_id: string;
  consumer_id: string;
  limit: number;
  reason: string;
  is_active: boolean;
  request_count: number;
}

interface RateLimitOverrideCardProps {
  overrides: OverrideInfo[];
  appName: string;
}

export default function RateLimitOverrideCard({ overrides, appName }: RateLimitOverrideCardProps) {
  const active = overrides.filter((o) => o.is_active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⚡ Rate Overrides
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">
          {active}/{overrides.length} active
        </span>
      </div>

      {overrides.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limit overrides</p>
      ) : (
        <div className="space-y-1.5">
          {overrides.map((o) => (
            <div
              key={o.override_id}
              className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!o.is_active ? "opacity-50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {o.consumer_id}
                </span>
                <span className="text-[11px] text-gray-400">{o.limit}/min</span>
              </div>
              <div className="mt-0.5 flex justify-between text-[10px] text-gray-400">
                {o.reason && <span>{o.reason}</span>}
                <span>{o.request_count} used</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
