"use client";
export function FleetAiAudiogenPanel({ services, active, clips, hours }: { services: number; active: number; clips: number; hours: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎵 AI Audio Gen</h3>
    <div className="text-sm">{active}/{services} active · {clips.toLocaleString()} clips · {hours.toLocaleString()}h generated</div>
  </div>);
}
