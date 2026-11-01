"use client";
export function FleetSdkAnalyticsV9Panel({ sdks, downloads }: { sdks: number; downloads: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 SDK Analytics v9</h3>
    <div className="text-sm">{sdks} SDKs · {downloads.toLocaleString()} downloads</div>
  </div>);
}
