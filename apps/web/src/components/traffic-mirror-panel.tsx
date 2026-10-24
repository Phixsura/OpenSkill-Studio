"use client";

interface Mirror { source: string; target: string; sampleRate: number;
  mirrored: number; errors: number; status: string; }
interface TrafficMirrorPanelProps { mirrors: Mirror[]; totalMirrored: number; active: number; }

export function TrafficMirrorPanel({ mirrors, totalMirrored, active }: TrafficMirrorPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪞 Traffic Mirroring</h3>
        <span className="text-xs text-gray-400">{active} active · {totalMirrored} mirrored</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {mirrors.map(m => (
          <div key={`${m.source}→${m.target}`} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-xs font-mono">{m.source} → {m.target}</div>
              <div className="text-[10px] text-gray-400">{m.sampleRate * 100}% sampled · {m.mirrored} mirrored</div>
            </div>
            <span className={`text-[10px] ${m.status === "active" ? "text-green-600" : "text-gray-400"}`}>● {m.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
