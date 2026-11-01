"use client";
export function FleetAiPlatSecV4Panel({ systems, active, score, threats, zeroTrust, encrypted }: { systems: number; active: number; score: number; threats: number; zeroTrust: boolean; encrypted: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Security v4</h3>
    <div className="text-sm">{active}/{systems} active · score {score} · {threats} threats · {zeroTrust ? "✅ ZT" : "⚠️"} · {encrypted}% encrypted</div>
  </div>);
}
