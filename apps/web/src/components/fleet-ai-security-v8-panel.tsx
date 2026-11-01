"use client";
export function FleetAiSecurityV8Panel({ systems, active, score, threats, zt, encrypted }: { systems: number; active: number; score: number; threats: number; zt: boolean; encrypted: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Security v8</h3>
    <div className="text-sm">{active}/{systems} active · score {score} · {threats.toLocaleString()} threats · {zt ? "✅ ZT" : "⚠️"} · {encrypted}% encrypted</div>
  </div>);
}
