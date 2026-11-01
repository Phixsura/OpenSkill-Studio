"use client";
interface ReqSamplingPanelProps { totalSeen: number; captured: number; sampleRate: number; }
export function ReqSamplingPanel({ totalSeen, captured, sampleRate }: ReqSamplingPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Request Sampling</h3>
        <span className="text-xs text-gray-400">{(sampleRate * 100).toFixed(1)}% rate · {captured} captured</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Seen</span><div className="font-bold text-lg">{totalSeen.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Captured</span><div className="font-bold text-blue-500 text-lg">{captured}</div></div>
        <div><span className="text-gray-400">Rate</span><div className="font-bold text-lg">{(sampleRate * 100).toFixed(1)}%</div></div>
      </div>
    </div>
  );
}
