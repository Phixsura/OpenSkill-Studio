"use client";
interface FlowProfilePanelProps { totalMs: number; spans: number; bottleneck: string;
  bottleneckMs: number; overheadMs: number; efficiencyPct: number; }
export function FlowProfilePanel({ totalMs, spans, bottleneck, bottleneckMs, overheadMs, efficiencyPct }: FlowProfilePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Flow Profile</h3>
        <span className="text-xs text-gray-400">{totalMs}ms · {spans} spans · {efficiencyPct}% efficient</span>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Total</span><div className="font-bold text-lg">{totalMs}ms</div></div>
        <div><span className="text-gray-400">Bottleneck</span><div className="font-bold text-red-500">{bottleneck}</div><div className="text-[10px]">{bottleneckMs}ms</div></div>
        <div><span className="text-gray-400">Overhead</span><div className="font-bold text-lg">{overheadMs}ms</div></div>
        <div><span className="text-gray-400">Efficiency</span><div className="font-bold text-lg">{efficiencyPct}%</div></div>
      </div>
    </div>
  );
}
