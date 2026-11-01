"use client";
export function FleetTraceSamplerPanel({ totalSpans, sampledPerSec, sampleRate, adequate }: { totalSpans: number; sampledPerSec: number; sampleRate: number; adequate: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Trace Sampling</h3>
    <div className="text-sm">{sampleRate}% rate · {sampledPerSec.toLocaleString()}/{totalSpans.toLocaleString()} spans/s</div>
    {!adequate && <span className="text-xs text-yellow-600">⚠️ Low sample rate</span>}
  </div>);
}
