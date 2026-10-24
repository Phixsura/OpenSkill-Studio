"use client";
export function FleetAiRespAiPanel({ frameworks, active, assessments, principles, compliance }: { frameworks: number; active: number; assessments: number; principles: number; compliance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 Responsible AI</h3>
    <div className="text-sm">{active}/{frameworks} active · {assessments} assessments · {principles} principles · {compliance}% compliant</div>
  </div>);
}
