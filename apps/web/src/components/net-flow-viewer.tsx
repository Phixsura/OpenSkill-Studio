"use client";

interface Flow { src: string; dst: string; bytes: number; packets: number; }
interface NetFlowViewerProps { totalFlows: number; uniquePairs: number;
  totalBytes: number; topFlows: Flow[]; }

export function NetFlowViewer({ totalFlows, uniquePairs, totalBytes, topFlows }: NetFlowViewerProps) {
  const maxBytes = Math.max(...topFlows.map(f => f.bytes), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌐 Network Flows</h3>
        <span className="text-xs text-gray-400">{uniquePairs} pairs · {(totalBytes / 1024).toFixed(0)} KB</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {topFlows.map(f => (
          <div key={`${f.src}→${f.dst}`} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{f.src} → {f.dst}</span>
              <span className="text-gray-400">{f.bytes.toLocaleString()} B · {f.packets} pkts</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(f.bytes / maxBytes) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
