"use client";
export function FleetApiComplianceCheckV9Panel({ checks, passed }: { checks: number; passed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">✅ API Compliance Check v9</h3>
    <div className="text-sm">{checks} checks · {passed} passed</div>
  </div>);
}
