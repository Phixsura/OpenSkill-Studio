"use client";
export function FleetSnowflakePanel({ warehouses, running, credits, queries }: { warehouses: number; running: number; credits: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">❄️ Snowflake</h3>
    <div className="text-sm">{running}/{warehouses} running · {credits} credits · {queries.toLocaleString()} queries</div>
  </div>);
}
