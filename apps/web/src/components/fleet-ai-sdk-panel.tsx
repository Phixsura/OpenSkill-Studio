"use client";
export function FleetAiSdkPanel({ sdks, languages, downloads, activeUsers }: { sdks: number; languages: number; downloads: number; activeUsers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI SDK</h3>
    <div className="text-sm">{sdks} SDKs · {languages} languages · {downloads.toLocaleString()} downloads · {activeUsers.toLocaleString()} users</div>
  </div>);
}
