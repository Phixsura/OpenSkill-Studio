"use client";
export function FleetAiRespStreamPanel({ streamers, active, streams, tokens, ttft }: { streamers: number; active: number; streams: number; tokens: number; ttft: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌊 AI Response Streamer</h3>
    <div className="text-sm">{active}/{streamers} active · {streams.toLocaleString()} streams · {tokens.toLocaleString()} tokens · TTFT {ttft}ms</div>
  </div>);
}
