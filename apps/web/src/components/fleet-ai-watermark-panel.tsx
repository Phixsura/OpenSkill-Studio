"use client";
export function FleetAiWatermarkPanel({ systems, active, watermarked, detected, rate }: { systems: number; active: number; watermarked: number; detected: number; rate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💧 AI Watermark</h3>
    <div className="text-sm">{active}/{systems} active · {watermarked.toLocaleString()} marked · {rate}% detection</div>
  </div>);
}
