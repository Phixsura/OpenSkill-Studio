"use client";
export function FleetGroqPanel({ endpoints, active, tokensPerSec, requests }: { endpoints: number; active: number; tokensPerSec: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Groq</h3>
    <div className="text-sm">{active}/{endpoints} active · {tokensPerSec.toLocaleString()} tok/s · {requests.toLocaleString()} req</div>
  </div>);
}
