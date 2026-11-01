"use client";
export function FleetNpsPanel({ responses, nps, excellent }: { responses: number; nps: number; excellent: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">😊 Platform NPS</h3>
    <div className={`text-2xl font-bold ${excellent ? "text-green-600" : nps >= 0 ? "text-blue-500" : "text-red-500"}`}>{nps}</div>
    <div className="text-xs text-gray-400">{responses} responses</div>
  </div>);
}
