"use client";
export function FleetContainerImageV9Panel({ images, scanned }: { images: number; scanned: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Container Image v9</h3>
    <div className="text-sm">{images} images · {scanned} scanned</div>
  </div>);
}
