"use client";
export function FleetAiVideogenPanel({ services, active, videos, minutes }: { services: number; active: number; videos: number; minutes: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎬 AI Video Gen</h3>
    <div className="text-sm">{active}/{services} active · {videos.toLocaleString()} videos · {minutes.toLocaleString()} min generated</div>
  </div>);
}
