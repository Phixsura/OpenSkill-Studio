"use client";
export function FleetAiSdkGenPanel({ generators, active, sdks, languages, downloads }: { generators: number; active: number; sdks: number; languages: number; downloads: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧰 AI SDK Generator</h3>
    <div className="text-sm">{active}/{generators} active · {sdks} SDKs · {languages} langs · {downloads.toLocaleString()} downloads</div>
  </div>);
}
