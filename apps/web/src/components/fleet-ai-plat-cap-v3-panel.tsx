"use client";
export function FleetAiPlatCapV3Panel({ planners, active, forecasts, accuracy, headroom }: { planners: number; active: number; forecasts: number; accuracy: number; headroom: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 AI Capacity v3</h3>
    <div className="text-sm">{active}/{planners} active · {forecasts} forecasts · {accuracy}% acc · {headroom}% headroom</div>
  </div>);
}
