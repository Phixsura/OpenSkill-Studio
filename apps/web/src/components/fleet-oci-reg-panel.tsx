"use client";
export function FleetOciRegPanel({ registries, healthy, images, storageGb }: { registries: number; healthy: number; images: number; storageGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 OCI Registry</h3>
    <div className="text-sm">{healthy}/{registries} healthy · {images.toLocaleString()} images · {storageGb}GB</div>
  </div>);
}
