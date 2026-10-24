"use client";
interface PayloadCompressPanelProps { originalBytes: number; compressedBytes: number;
  ratioPct: number; totalCompressed: number; }
export function PayloadCompressPanel({ originalBytes, compressedBytes, ratioPct, totalCompressed }: PayloadCompressPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗜️ Payload Compression</h3>
        <span className="text-xs text-green-600 font-bold">{ratioPct}% saved · {totalCompressed} compressed</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Original</span><div className="font-bold text-lg">{(originalBytes / 1024).toFixed(1)}KB</div></div>
        <div><span className="text-gray-400">Compressed</span><div className="font-bold text-green-600 text-lg">{(compressedBytes / 1024).toFixed(1)}KB</div></div>
      </div>
    </div>
  );
}
