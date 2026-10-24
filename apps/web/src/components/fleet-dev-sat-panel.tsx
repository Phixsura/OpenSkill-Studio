"use client";
export function FleetDevSatPanel({ responses, avgScore, happyPct, good }: { responses: number; avgScore: number; happyPct: number; good: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">😊 Dev Satisfaction</h3>
    <div className={`text-lg font-bold ${good ? "text-green-600" : "text-yellow-600"}`}>{avgScore}/5 · {happyPct}% happy</div>
    <div className="text-xs text-gray-400">{responses} responses</div>
  </div>);
}
