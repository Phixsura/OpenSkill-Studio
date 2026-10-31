"use client";
export function FleetImgVulnPanel({ images, critical, high, clean }: { images: number; critical: number; high: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Image Vulnerabilities</h3>
    {clean ? <span className="text-xs text-green-600">✅ {images} images clean</span>
     : <span className="text-xs text-red-500">⚠️ {critical} critical · {high} high across {images} images</span>}
  </div>);
}
