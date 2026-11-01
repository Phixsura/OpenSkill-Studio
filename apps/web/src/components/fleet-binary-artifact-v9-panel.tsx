"use client";
export function FleetBinaryArtifactV9Panel({ artifacts, downloads }: { artifacts: number; downloads: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📀 Binary Artifact v9</h3>
    <div className="text-sm">{artifacts} artifacts · {downloads.toLocaleString()} downloads</div>
  </div>);
}
