"use client";
export function FleetCoherePanel({ endpoints, active, embedCalls, generateCalls }: { endpoints: number; active: number; embedCalls: number; generateCalls: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧠 Cohere</h3>
    <div className="text-sm">{active}/{endpoints} active · {embedCalls.toLocaleString()} embeds · {generateCalls.toLocaleString()} generates</div>
  </div>);
}
