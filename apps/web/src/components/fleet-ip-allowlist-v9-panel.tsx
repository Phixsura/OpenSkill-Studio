"use client";
export function FleetIpAllowlistV9Panel({ rules, blocked }: { rules: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 IP Allowlist v9</h3>
    <div className="text-sm">{rules} rules · {blocked} blocked today</div>
  </div>);
}
