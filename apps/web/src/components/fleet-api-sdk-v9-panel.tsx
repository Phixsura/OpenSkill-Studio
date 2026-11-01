"use client";
export function FleetApiSdkV9Panel({ sdks, languages }: { sdks: number; languages: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 API SDK v9</h3>
    <div className="text-sm">{sdks} SDKs · {languages} languages</div>
  </div>);
}
