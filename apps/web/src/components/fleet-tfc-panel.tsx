"use client";
export function FleetTfcPanel({ total, applied, errored, monthlyCost }: { total: number; applied: number; errored: number; monthlyCost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Terraform Cloud</h3>
    <div className="text-sm">{applied}✅ {errored}❌ · ${monthlyCost.toLocaleString()}/mo</div>
  </div>);
}
