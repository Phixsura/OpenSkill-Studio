"use client";
export function FleetAiModelDiscV2Panel({ engines, active, searches, models, recommendations }: { engines: number; active: number; searches: number; models: number; recommendations: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 AI Model Discovery v2</h3>
    <div className="text-sm">{active}/{engines} active · {searches.toLocaleString()} searches · {models} models · {recommendations.toLocaleString()} recs</div>
  </div>);
}
