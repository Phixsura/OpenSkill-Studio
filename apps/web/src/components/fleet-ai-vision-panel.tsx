"use client";
export function FleetAiVisionPanel({ pipelines, active, images, accuracy, models }: { pipelines: number; active: number; images: number; accuracy: number; models: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ AI Vision</h3>
    <div className="text-sm">{active}/{pipelines} active · {images.toLocaleString()} images · {accuracy}% acc · {models} models</div>
  </div>);
}
