"use client";
export function FleetAiImagegenPanel({ services, active, images, avgGenSec }: { services: number; active: number; images: number; avgGenSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖼️ AI Image Gen</h3>
    <div className="text-sm">{active}/{services} active · {images.toLocaleString()} images · {avgGenSec}s avg</div>
  </div>);
}
