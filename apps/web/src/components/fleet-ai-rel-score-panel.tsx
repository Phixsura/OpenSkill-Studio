"use client";
export function FleetAiRelScorePanel({ scorers, active, score, availability, durability }: { scorers: number; active: number; score: number; availability: number; durability: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏆 AI Reliability Score</h3>
    <div className="text-sm">{active}/{scorers} active · score {score} · avail {availability}% · durability {durability}%</div>
  </div>);
}
