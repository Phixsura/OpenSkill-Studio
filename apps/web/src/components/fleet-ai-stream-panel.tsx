"use client";
export function FleetAiStreamPanel({ endpoints, active, activeStreams, tokensStreamed }: { endpoints: number; active: number; activeStreams: number; tokensStreamed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌊 AI Streaming</h3>
    <div className="text-sm">{active}/{endpoints} active · {activeStreams.toLocaleString()} streams · {tokensStreamed.toLocaleString()} tokens</div>
  </div>);
}
