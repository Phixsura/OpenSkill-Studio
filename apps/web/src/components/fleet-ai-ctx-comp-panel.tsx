"use client";
export function FleetAiCtxCompPanel({ compressors, active, compressions, ratio, quality }: { compressors: number; active: number; compressions: number; ratio: number; quality: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗜️ AI Context Compressor</h3>
    <div className="text-sm">{active}/{compressors} active · {compressions.toLocaleString()} compressions · {ratio}x ratio · {quality}% quality</div>
  </div>);
}
