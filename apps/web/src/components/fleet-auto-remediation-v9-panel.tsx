"use client";
export function FleetAutoRemediationV9Panel({ rules, triggered }: { rules: number; triggered: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 Auto Remediation v9</h3>
    <div className="text-sm">{rules} rules · {triggered} triggered today</div>
  </div>);
}
