"use client";
export function FleetAiDistillPanel({ jobs, active, teacherB, studentB, retention }: { jobs: number; active: number; teacherB: number; studentB: number; retention: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI Distillation</h3>
    <div className="text-sm">{active}/{jobs} active · {teacherB}B→{studentB}B params · {retention}% retained</div>
  </div>);
}
