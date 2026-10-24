"use client";
interface Transition { from: string; to: string; reason: string; }
interface CircuitFsmPanelProps { state: string; failures: number; transitions: Transition[]; }
const STATE_COLOR: Record<string, string> = { closed: "bg-green-500", open: "bg-red-500", half_open: "bg-yellow-500" };
export function CircuitFsmPanel({ state, failures, transitions }: CircuitFsmPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Circuit FSM</h3>
        <div className="flex items-center gap-2">
          <span className={`w-3 h-3 rounded-full ${STATE_COLOR[state] ?? "bg-gray-400"}`} />
          <span className="text-xs font-bold">{state} · {failures} failures</span>
        </div>
      </div>
      {transitions.length > 0 && (
        <div className="p-3 text-xs text-gray-400 space-y-0.5">
          {transitions.map((t, i) => (
            <div key={i}>{t.from} → {t.to} <span className="text-gray-500">({t.reason})</span></div>
          ))}
        </div>
      )}
    </div>
  );
}
