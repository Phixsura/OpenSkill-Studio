"use client";
export function FleetAiMultimodalPanel({ services, active, imageCalls, audioCalls, videoCalls, totalCalls }: { services: number; active: number; imageCalls: number; audioCalls: number; videoCalls: number; totalCalls: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎨 AI Multimodal</h3>
    <div className="text-sm">{active}/{services} active · 🖼️ {imageCalls.toLocaleString()} · 🔊 {audioCalls.toLocaleString()} · 🎬 {videoCalls.toLocaleString()}</div>
  </div>);
}
