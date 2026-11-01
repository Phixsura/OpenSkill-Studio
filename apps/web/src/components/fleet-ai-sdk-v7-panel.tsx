"use client";
export function FleetAiSdkV7Panel({ sdks, active, languages, downloads, stars }: { sdks: number; active: number; languages: number; downloads: number; stars: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧰 AI SDK v7</h3>
    <div className="text-sm">{active}/{sdks} active · {languages} languages · {downloads.toLocaleString()} downloads · ⭐ {stars.toLocaleString()}</div>
  </div>);
}
