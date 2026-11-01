"use client";

interface CircuitInfo {
  name: string;
  state: "closed" | "open" | "half_open";
  failureCount: number;
  totalRequests: number;
  totalFailures: number;
  totalShortCircuits: number;
  failureRate: number;
}

const stateConfig: Record<string, { color: string; icon: string; label: string }> = {
  closed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "🟢", label: "Closed" },
  open: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "🔴", label: "Open" },
  half_open: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "🟡", label: "Half-Open" },
};

export function CircuitBreakerPanel({
  circuits,
  onForceOpen,
  onForceClose,
}: {
  circuits: CircuitInfo[];
  onForceOpen?: (name: string) => void;
  onForceClose?: (name: string) => void;
}) {
  const openCount = circuits.filter((c) => c.state === "open").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚡ Circuit Breakers</h2>
        {openCount > 0 && (
          <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{openCount} open</span>
        )}
      </div>

      <div className="space-y-2">
        {circuits.map((c) => {
          const cfg = stateConfig[c.state];
          return (
            <div key={c.name} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{c.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
                </div>
                <div className="flex gap-1">
                  {c.state !== "open" && (
                    <button onClick={() => onForceOpen?.(c.name)}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Trip</button>
                  )}
                  {c.state !== "closed" && (
                    <button onClick={() => onForceClose?.(c.name)}
                      className="text-xs bg-green-600 text-white px-2 py-1 rounded">Reset</button>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs text-center">
                <div>
                  <span className="text-gray-400 block">Requests</span>
                  <span className="font-bold">{c.totalRequests}</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Failures</span>
                  <span className="font-bold text-red-500">{c.totalFailures}</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Fail Rate</span>
                  <span className={`font-bold ${c.failureRate > 30 ? "text-red-600" : "text-green-600"}`}>{c.failureRate}%</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Rejected</span>
                  <span className="font-bold text-orange-500">{c.totalShortCircuits}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
