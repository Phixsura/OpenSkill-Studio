"use client";
export function FleetVercelAiPanel({ apps, deployed, streams, tokens }: { apps: number; deployed: number; streams: number; tokens: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">▲ Vercel AI</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {streams.toLocaleString()} streams · {tokens.toLocaleString()} tokens</div>
  </div>);
}
