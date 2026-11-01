"use client";
export function FleetApiTestingV9Panel({ suites, passed }: { suites: number; passed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 API Testing v9</h3>
    <div className="text-sm">{suites} suites · {passed} passed</div>
  </div>);
}
