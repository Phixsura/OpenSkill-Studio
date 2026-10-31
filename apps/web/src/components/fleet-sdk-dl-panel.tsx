"use client";
export function FleetSdkDlPanel({ totalDownloads, sdks, topSdk, topDownloads }: { totalDownloads: number; sdks: number; topSdk: string | null; topDownloads: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📥 SDK Downloads</h3>
    <div className="text-sm">{totalDownloads.toLocaleString()} total · {sdks} SDKs</div>
    {topSdk && <div className="text-xs text-blue-500">Top: {topSdk} ({topDownloads.toLocaleString()})</div>}
  </div>);
}
