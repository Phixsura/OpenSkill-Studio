"use client";
export function FleetApiUsageAnalyticsV9Panel({ apis, growing }: { apis: number; growing: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Usage Analytics v9</h3>
    <div className="text-sm">{apis} APIs · {growing} growing</div>
  </div>);
}
