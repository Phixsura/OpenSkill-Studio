"use client";

import { useState } from "react";

interface FunnelStage {
  name: string;
  count: number;
  conversionRate: number;
  dropOff?: number;
}

interface SourceBreakdown {
  source: string;
  stages: Record<string, number>;
}

export function AnalyticsFunnelChart({
  stages,
  sources,
  extensionName,
  totalUsers,
}: {
  stages: FunnelStage[];
  sources: SourceBreakdown[];
  extensionName: string;
  totalUsers: number;
}) {
  const [view, setView] = useState<"funnel" | "sources">("funnel");
  const maxCount = Math.max(...stages.map((s) => s.count), 1);

  const stageColors = [
    "bg-blue-500", "bg-indigo-500", "bg-purple-500", "bg-pink-500", "bg-green-500",
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📊 {extensionName} Funnel</h2>
        <span className="text-sm text-gray-500">{totalUsers} total users</span>
      </div>

      <div className="flex gap-1">
        {(["funnel", "sources"] as const).map((v) => (
          <button key={v} onClick={() => setView(v)}
            className={`text-xs px-3 py-1 rounded-lg ${view === v ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {v === "funnel" ? "Funnel" : "Sources"}
          </button>
        ))}
      </div>

      {view === "funnel" && (
        <div className="space-y-3">
          {stages.map((stage, i) => {
            const width = Math.max((stage.count / maxCount) * 100, 5);
            return (
              <div key={stage.name}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="font-medium capitalize">{stage.name}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-bold">{stage.count.toLocaleString()}</span>
                    <span className="text-gray-400 text-xs">{stage.conversionRate}%</span>
                    {stage.dropOff !== undefined && stage.dropOff > 0 && (
                      <span className="text-red-500 text-xs">↓{stage.dropOff}%</span>
                    )}
                  </div>
                </div>
                <div className="h-8 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                  <div className={`h-full ${stageColors[i % stageColors.length]} rounded-lg transition-all`}
                    style={{ width: `${width}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {view === "sources" && (
        <div className="space-y-2">
          {sources.map((src) => (
            <div key={src.source} className="rounded-lg border dark:border-gray-700 p-3">
              <span className="font-semibold text-sm capitalize">{src.source}</span>
              <div className="flex gap-3 mt-1 text-xs text-gray-500">
                {Object.entries(src.stages).map(([stage, count]) => (
                  <span key={stage}>{stage}: <b>{count}</b></span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
