"use client";
interface GoldenPathPanelProps { goldenPath: string[]; actualPath: string[];
  followsGolden: boolean; deviations: number; }
export function GoldenPathPanel({ goldenPath, actualPath, followsGolden, deviations }: GoldenPathPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛤️ Golden Path</h3>
        <span className={`text-xs font-bold ${followsGolden ? "text-green-600" : "text-yellow-600"}`}>
          {followsGolden ? "✅ On golden path" : `⚠ ${deviations} deviations`}
        </span>
      </div>
      <div className="p-4 space-y-2 text-xs">
        <div><span className="text-gray-400">Golden:</span> <span className="font-mono">{goldenPath.join(" → ")}</span></div>
        <div><span className="text-gray-400">Actual:</span> <span className={`font-mono ${followsGolden ? "text-green-600" : "text-yellow-600"}`}>{actualPath.join(" → ")}</span></div>
      </div>
    </div>
  );
}
