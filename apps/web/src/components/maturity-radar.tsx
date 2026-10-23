"use client";

interface Dimension { dimension: string; name: string; level: number; levelName: string; maxLevel: number; }
interface MaturityRadarProps { overallLevel: number; overallName: string; averageScore: number;
  dimensions: Dimension[]; strengths: string[]; improvements: string[]; }

const LEVEL_COLOR: Record<number, string> = {
  1: "bg-red-500", 2: "bg-orange-500", 3: "bg-yellow-500", 4: "bg-blue-500", 5: "bg-green-500",
};

export function MaturityRadar({ overallLevel, overallName, averageScore, dimensions, strengths, improvements }: MaturityRadarProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="text-center mb-5">
        <h3 className="font-semibold mb-2">🎯 Platform Maturity</h3>
        <p className="text-4xl font-bold">{averageScore}<span className="text-lg text-gray-300">/5</span></p>
        <p className="text-sm text-gray-400">Level {overallLevel}: {overallName}</p>
      </div>
      <div className="space-y-2 mb-4">
        {dimensions.map(d => (
          <div key={d.dimension}>
            <div className="flex justify-between text-sm mb-1">
              <span>{d.name}</span>
              <span className="text-xs text-gray-400">L{d.level} {d.levelName}</span>
            </div>
            <div className="flex gap-1">
              {Array.from({ length: d.maxLevel }, (_, i) => (
                <div key={i} className={`h-2 flex-1 rounded ${i < d.level ? LEVEL_COLOR[d.level] : "bg-gray-200 dark:bg-gray-700"}`} />
              ))}
            </div>
          </div>
        ))}
      </div>
      {strengths.length > 0 && (
        <p className="text-xs text-green-600 mb-1">💪 Strengths: {strengths.join(", ")}</p>
      )}
      {improvements.length > 0 && (
        <p className="text-xs text-yellow-600">📈 Improve: {improvements.join(", ")}</p>
      )}
    </div>
  );
}
