"use client";
export function FleetDynamodbPanel({ tables, active, throttled, consumedRcu }: { tables: number; active: number; throttled: number; consumedRcu: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ DynamoDB</h3>
    <div className="text-sm">{active}/{tables} active · {consumedRcu.toLocaleString()} RCU</div>
    {throttled > 0 && <span className="text-xs text-yellow-600">⚠️ {throttled} throttled</span>}
  </div>);
}
