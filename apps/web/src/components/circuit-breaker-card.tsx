"use client";

interface BreakerInfo {
  breaker_id: string;
  service_name: string;
  state: "closed" | "open" | "half_open";
  failure_count: number;
  failure_threshold: number;
  success_count: number;
}

interface CircuitBreakerCardProps {
  breakers: BreakerInfo[];
  appName: string;
}

const stateStyle: Record<string, string> = {
  closed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  open: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  half_open: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
};

export default function CircuitBreakerCard({ breakers, appName }: CircuitBreakerCardProps) {
  const openCount = breakers.filter((b) => b.state === "open").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ⚡ Circuit Breakers
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{breakers.length} breakers</span>
          {openCount > 0 && (
            <p className="text-[10px] font-medium text-red-600 dark:text-red-400">
              {openCount} open
            </p>
          )}
        </div>
      </div>

      {breakers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuit breakers</p>
      ) : (
        <div className="space-y-1.5">
          {breakers.map((b) => (
            <div
              key={b.breaker_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                  {b.service_name}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${stateStyle[b.state] ?? ""}`}
                >
                  {b.state.replace("_", " ")}
                </span>
              </div>
              <div className="mt-1 flex justify-between text-[10px] text-gray-400">
                <span>
                  {b.failure_count}/{b.failure_threshold} failures
                </span>
                <span>{b.success_count} successes</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
