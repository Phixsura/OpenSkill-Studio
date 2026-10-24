"use client";
export function FleetSonarqubePanel({ total, passing, failing, avgCoverage }: { total: number; passing: number; failing: number; avgCoverage: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 SonarQube</h3>
    <div className="text-sm">{passing}/{total} passing · {avgCoverage}% coverage</div>
    {failing > 0 && <span className="text-xs text-red-500">❌ {failing} failing gates</span>}
  </div>);
}
