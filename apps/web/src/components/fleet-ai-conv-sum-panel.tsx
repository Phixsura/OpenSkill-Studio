"use client";
export function FleetAiConvSumPanel({ summarizers, active, summarized, compression, retention }: { summarizers: number; active: number; summarized: number; compression: number; retention: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Conversation Summarizer</h3>
    <div className="text-sm">{active}/{summarizers} active · {summarized.toLocaleString()} summarized · {compression}x · {retention}% retention</div>
  </div>);
}
