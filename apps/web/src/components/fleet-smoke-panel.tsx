"use client";
export function FleetSmokePanel({ total, passed, failed, allPassed }: { total: number; passed: number; failed: number; allPassed: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💨 Smoke Tests</h3>
    {allPassed ? <span className="text-xs text-green-600">✅ All {total} passed</span>
     : <span className="text-xs text-red-500">❌ {failed}/{total} failed</span>}
  </div>);
}
