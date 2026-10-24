"use client";
export function FleetAiWatermarkPanel({ services, active, watermarked, verified }: { services: number; active: number; watermarked: number; verified: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💧 AI Watermark</h3>
    <div className="text-sm">{active}/{services} active · {watermarked.toLocaleString()} marked · {verified.toLocaleString()} verified</div>
  </div>);
}
