"use client";
export function FleetGdprPanel({ total, met, unmet, score, compliant }: { total: number; met: number; unmet: number; score: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🇪🇺 GDPR</h3>
    <div className={`text-lg font-bold ${compliant ? "text-green-600" : "text-yellow-600"}`}>{score}%</div>
    <div className="text-xs text-gray-400">{met}/{total} controls met</div>
  </div>);
}
