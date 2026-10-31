"use client";
export function FleetAi3dGenPanel({ generators, active, models, avgPolys, textured }: { generators: number; active: number; models: number; avgPolys: number; textured: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧊 AI 3D Generation</h3>
    <div className="text-sm">{active}/{generators} active · {models.toLocaleString()} models · {avgPolys.toLocaleString()} polys · {textured} textured</div>
  </div>);
}
