"use client";
export function FleetLangchainPanel({ apps, deployed, chains, traces }: { apps: number; deployed: number; chains: number; traces: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦜 LangChain</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {chains} chains · {traces.toLocaleString()} traces</div>
  </div>);
}
