"use client";
export function FleetAiKnowBasePanel({ bases, active, articles, searches, helpful }: { bases: number; active: number; articles: number; searches: number; helpful: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 AI Knowledge Base</h3>
    <div className="text-sm">{active}/{bases} active · {articles.toLocaleString()} articles · {searches.toLocaleString()} searches · {helpful}% helpful</div>
  </div>);
}
