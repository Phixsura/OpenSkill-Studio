"use client";

interface SpanSamplerPanelProps { sampled: number; dropped: number; actualRatePct: number;
  configuredRate: number; strategy: string; }

export function SpanSamplerPanel({ sampled, dropped, actualRatePct, configuredRate, strategy }: SpanSamplerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎲 Span Sampler</h3>
        <span className="text-xs text-gray-400">{strategy} · {(configuredRate * 100).toFixed(0)}% configured</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Sampled</div><div className="font-bold text-green-600 text-lg">{sampled.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Dropped</div><div className="font-bold text-gray-400 text-lg">{dropped.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Actual Rate</div><div className="font-bold text-lg">{actualRatePct}%</div></div>
      </div>
    </div>
  );
}
