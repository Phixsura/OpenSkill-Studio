"use client";
interface EventDedupPanelProps { seen: number; deduped: number; window: number; }
export function EventDedupPanel({ seen, deduped, window }: EventDedupPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Event Dedup</h3>
        <span className="text-xs text-gray-400">{seen}/{window} tracked · {deduped} deduped</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Seen</span><div className="font-bold text-lg">{seen.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Deduped</span><div className="font-bold text-yellow-600 text-lg">{deduped.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Window</span><div className="font-bold text-lg">{window.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
