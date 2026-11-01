"use client";
export function FleetAiSentimentPanel({ analyzers, active, analyzed, accuracy, emotions }: { analyzers: number; active: number; analyzed: number; accuracy: number; emotions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">😊 AI Sentiment</h3>
    <div className="text-sm">{active}/{analyzers} active · {analyzed.toLocaleString()} analyzed · {accuracy}% acc · {emotions} emotions</div>
  </div>);
}
