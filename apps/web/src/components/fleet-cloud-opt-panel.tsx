"use client";
export function FleetCloudOptPanel({ totalRecs, implemented, pending, totalSavings, realizedSavings }: { totalRecs: number; implemented: number; pending: number; totalSavings: number; realizedSavings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Optimization</h3>
    <div className="text-sm">{implemented}/{totalRecs} implemented · ${realizedSavings.toLocaleString()}/mo saved</div>
    {pending > 0 && <span className="text-xs text-green-600">💰 ${(totalSavings - realizedSavings).toLocaleString()}/mo more available</span>}
  </div>);
}
