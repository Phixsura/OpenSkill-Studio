"use client";
export function FleetAiSentimentPanel({ services, active, analyses, positivePct }: { services: number; active: number; analyses: number; positivePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">😊 AI Sentiment</h3>
    <div className="text-sm">{active}/{services} active · {analyses.toLocaleString()} analyses · {positivePct}% positive</div>
  </div>);
}
