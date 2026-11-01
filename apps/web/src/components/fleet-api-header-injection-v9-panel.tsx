"use client";
export function FleetApiHeaderInjectionV9Panel({ endpoints, blocked }: { endpoints: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Header Injection v9</h3>
    <div className="text-sm">{endpoints} endpoints · {blocked} blocked</div>
  </div>);
}
