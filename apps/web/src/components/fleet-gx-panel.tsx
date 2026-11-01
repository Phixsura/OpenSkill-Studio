"use client";
export function FleetGxPanel({ projects, active, expectations, validations, successRate }: { projects: number; active: number; expectations: number; validations: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ Great Expectations</h3>
    <div className="text-sm">{active}/{projects} active · {expectations} exps · {validations.toLocaleString()} validations · {successRate}%</div>
  </div>);
}
