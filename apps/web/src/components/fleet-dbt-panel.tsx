"use client";
export function FleetDbtPanel({ projects, passing, failed, models, tests }: { projects: number; passing: number; failed: number; models: number; tests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 dbt</h3>
    <div className="text-sm">{passing}/{projects} passing · {models} models · {tests} tests</div>
    {failed > 0 && <span className="text-xs text-red-500">❌ {failed} failed</span>}
  </div>);
}
