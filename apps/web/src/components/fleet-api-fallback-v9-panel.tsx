"use client";
export function FleetApiFallbackV9Panel({ fallbacks, triggered }: { fallbacks: number; triggered: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 API Fallback v9</h3>
    <div className="text-sm">{fallbacks} fallbacks · {triggered} triggered</div>
  </div>);
}
