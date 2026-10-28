"use client";

interface RatePlanInfo {
  plan_id: string;
  name: string;
  requests_per_minute: number;
  requests_per_hour: number;
  requests_per_day: number;
}

interface APIRatePlanCardProps {
  plans: RatePlanInfo[];
  appName: string;
}

export default function APIRatePlanCard({ plans, appName }: APIRatePlanCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Rate Plans</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{plans.length} plans</span>
      </div>

      {plans.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate plans</p>
      ) : (
        <div className="space-y-2">
          {plans.map((p) => (
            <div
              key={p.plan_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <p className="text-xs font-medium text-gray-800 dark:text-gray-200">{p.name}</p>
              <div className="mt-1 flex gap-3 text-[10px] text-gray-400">
                <span>{p.requests_per_minute}/min</span>
                <span>{p.requests_per_hour.toLocaleString()}/hr</span>
                <span>{p.requests_per_day.toLocaleString()}/day</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
