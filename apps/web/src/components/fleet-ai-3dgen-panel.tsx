"use client";
export function FleetAi3dgenPanel({ services, active, models, vertices }: { services: number; active: number; models: number; vertices: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧊 AI 3D Gen</h3>
    <div className="text-sm">{active}/{services} active · {models.toLocaleString()} models · {vertices.toLocaleString()} vertices</div>
  </div>);
}
