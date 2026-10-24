"use client";
interface MirrorInfo { source: string; target: string; active: boolean; mirrored: number; samplePct: number; }
interface TrafficMirrorPanelProps { mirrors: MirrorInfo[]; totalMirrored: number; }
export function TrafficMirrorPanel({ mirrors, totalMirrored }: TrafficMirrorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪞 Traffic Mirror</h3>
        <span className="text-xs text-gray-400">{mirrors.length} mirrors · {totalMirrored.toLocaleString()} mirrored</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {mirrors.map(m => (
          <div key={`${m.source}→${m.target}`} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{m.source} → {m.target}</span>
            <div className="flex items-center gap-2 text-gray-400">
              <span>{m.samplePct}%</span>
              <span>{m.mirrored.toLocaleString()}</span>
              <span className={`w-2 h-2 rounded-full ${m.active ? "bg-green-500" : "bg-gray-400"}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
