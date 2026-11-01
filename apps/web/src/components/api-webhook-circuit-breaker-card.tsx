"use client";

interface BreakerInfo {
  destination: string;
  state: "closed" | "open" | "half_open";
  consecutive_failures: number;
  failure_threshold: number;
}

interface APIWebhookCircuitBreakerCardProps {
  breakers: BreakerInfo[];
  appName: string;
}

const stateStyle: Record<string, string> = {
  closed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  open: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  half_open: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
};

export default function APIWebhookCircuitBreakerCard({ breakers, appName }: APIWebhookCircuitBreakerCardProps) {
  const open = breakers.filter((b) => b.state === "open").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Webhook Breakers</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{breakers.length} destinations</span>
          {open > 0 && <p className="text-[10px] text-red-500">{open} open</p>}
        </div>
      </div>

      {breakers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No circuit breakers</p>
      ) : (
        <div className="space-y-1">
          {breakers.map((b) => (
            <div key={b.destination} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${stateStyle[b.state]}`}>{b.state.replace("_", " ")}</span>
                <span className="truncate max-w-[150px] text-gray-700 dark:text-gray-300">{b.destination}</span>
              </div>
              <span className="text-gray-400">{b.consecutive_failures}/{b.failure_threshold}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
