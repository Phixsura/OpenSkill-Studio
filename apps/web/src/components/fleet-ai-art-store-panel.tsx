"use client";
export function FleetAiArtStorePanel({ stores, active, artifacts, sizeTb, downloads }: { stores: number; active: number; artifacts: number; sizeTb: number; downloads: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 AI Artifact Store</h3>
    <div className="text-sm">{active}/{stores} active · {artifacts.toLocaleString()} artifacts · {sizeTb}TB · {downloads.toLocaleString()} downloads</div>
  </div>);
}
