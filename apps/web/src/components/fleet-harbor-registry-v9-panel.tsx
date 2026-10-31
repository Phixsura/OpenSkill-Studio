"use client";
export function FleetHarborRegistryV9Panel({ registries, images }: { registries: number; images: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚓ Harbor Registry v9</h3>
    <div className="text-sm">{registries} registries · {images} images</div>
  </div>);
}
