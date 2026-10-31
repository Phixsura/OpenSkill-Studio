"use client";
interface IdemHandlerPanelProps { storedResults: number; ttlSeconds: number; cacheHits: number; }
export function IdemHandlerPanel({ storedResults, ttlSeconds, cacheHits }: IdemHandlerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 Idempotent Handler</h3>
        <span className="text-xs text-gray-400">{storedResults} stored · {ttlSeconds}s TTL · {cacheHits} hits</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Stored</span><div className="font-bold text-lg">{storedResults}</div></div>
        <div><span className="text-gray-400">TTL</span><div className="font-bold text-lg">{ttlSeconds}s</div></div>
        <div><span className="text-gray-400">Hits</span><div className="font-bold text-green-600 text-lg">{cacheHits}</div></div>
      </div>
    </div>
  );
}
