"use client";
export function FleetEnvPromoterV9Panel({ promotions, blocked }: { promotions: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Env Promoter v9</h3>
    <div className="text-sm">{promotions} promotions · {blocked} blocked</div>
  </div>);
}
