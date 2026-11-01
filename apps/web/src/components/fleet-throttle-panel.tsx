"use client";
export function FleetThrottlePanel({ total, throttled, heavy, clean }: { total: number; throttled: number; heavy: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚦 API Throttling</h3>
    {clean ? <span className="text-xs text-green-600">✅ No tenants throttled</span>
     : <span className="text-xs text-yellow-600">⚠️ {throttled} throttled · {heavy} heavy</span>}
  </div>);
}
