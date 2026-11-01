"use client";
export function FleetAiImgGenPanel({ generators, active, images, latency, resolutions }: { generators: number; active: number; images: number; latency: number; resolutions: string[]; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎨 AI Image Generation</h3>
    <div className="text-sm">{active}/{generators} active · {images.toLocaleString()} images · {latency}s · {resolutions.join(", ")}</div>
  </div>);
}
