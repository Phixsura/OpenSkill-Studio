"use client";
export function FleetImageScanV9Panel({ images, clean }: { images: number; clean: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Image Scan v9</h3>
    <div className="text-sm">{images} images · {clean} clean</div>
  </div>);
}
