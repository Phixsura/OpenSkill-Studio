"use client";
export function FleetAiVisionPanel({ services, active, images, detections }: { services: number; active: number; images: number; detections: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ AI Vision</h3>
    <div className="text-sm">{active}/{services} active · {images.toLocaleString()} images · {detections.toLocaleString()} detections</div>
  </div>);
}
