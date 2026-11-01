"use client";
export function FleetConcoursePanel({ pipelines, paused, jobsPassing, jobsFailing }: { pipelines: number; paused: number; jobsPassing: number; jobsFailing: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✈️ Concourse</h3>
    <div className="text-sm">{pipelines} pipelines · {jobsPassing}✅ {jobsFailing}❌ jobs</div>
  </div>);
}
