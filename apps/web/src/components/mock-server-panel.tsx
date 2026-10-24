"use client";
interface MockEndpoint { key: string; status: number; calls: number; delayMs: number; }
interface MockServerPanelProps { mocks: MockEndpoint[]; totalCalls: number; }
export function MockServerPanel({ mocks, totalCalls }: MockServerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎭 Mock Server</h3>
        <span className="text-xs text-gray-400">{mocks.length} mocks · {totalCalls} calls</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {mocks.map(m => (
          <div key={m.key} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{m.key}</span>
            <span className="text-gray-400">{m.status} · {m.calls} calls{m.delayMs > 0 ? ` · ${m.delayMs}ms delay` : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
