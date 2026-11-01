"use client";
export function FleetAiSecV6Panel({ systems, active, score, threats, zt }: { systems: number; active: number; score: number; threats: number; zt: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Security v6</h3>
    <div className="text-sm">{active}/{systems} active · score {score} · {threats.toLocaleString()} threats · {zt ? "✅ ZT" : "⚠️"}</div>
  </div>);
}
