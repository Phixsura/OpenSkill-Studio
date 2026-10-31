"use client";
export function FleetAiUserAnalV2Panel({ dashboards, active, dau, mau, retention, engagement }: { dashboards: number; active: number; dau: number; mau: number; retention: number; engagement: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI User Analytics v2</h3>
    <div className="text-sm">{active}/{dashboards} active · {dau.toLocaleString()} DAU · {mau.toLocaleString()} MAU · {retention}% retention · {engagement}m engagement</div>
  </div>);
}
