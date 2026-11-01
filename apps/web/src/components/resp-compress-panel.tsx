"use client";
interface RespCompressPanelProps { compressionRate: number; compressed: number;
  totalRequests: number; savedMb: number; }
export function RespCompressPanel({ compressionRate, compressed, totalRequests, savedMb }: RespCompressPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗜️ Response Compression</h3>
        <span className="text-xs text-green-600 font-bold">{compressionRate}% compressed · {savedMb}MB saved</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Compressed</span><div className="font-bold text-lg">{compressed.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Total</span><div className="font-bold text-lg">{totalRequests.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
