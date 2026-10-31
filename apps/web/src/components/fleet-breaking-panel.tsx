"use client";
export function FleetBreakingPanel({ totalChanges, breaking, withGuide, safe }: { totalChanges: number; breaking: number; withGuide: number; safe: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💔 Breaking Changes</h3>
    {safe ? <span className="text-xs text-green-600">✅ No breaking changes</span>
     : <span className="text-xs text-red-500">⚠️ {breaking} breaking · {withGuide} with migration guide</span>}
  </div>);
}
