"use client";
export function FleetAiEthicsV7Panel({ systems, active, assessments, principles, score }: { systems: number; active: number; assessments: number; principles: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 AI Ethics v7</h3>
    <div className="text-sm">{active}/{systems} active · {assessments} assessments · {principles} principles · score {score}</div>
  </div>);
}
