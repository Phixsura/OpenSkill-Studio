"use client";
export function FleetAiDevSdkPanel({ sdks, active, languages, downloads, developers }: { sdks: number; active: number; languages: number; downloads: number; developers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧰 AI Developer SDK</h3>
    <div className="text-sm">{active}/{sdks} active · {languages} langs · {downloads.toLocaleString()} downloads · {developers.toLocaleString()} devs</div>
  </div>);
}
