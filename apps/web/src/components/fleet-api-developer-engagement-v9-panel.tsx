"use client";
export function FleetApiDeveloperEngagementV9Panel({ devs, nps }: { devs: number; nps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💻 Dev Engagement v9</h3>
    <div className="text-sm">{devs.toLocaleString()} devs · NPS {nps}</div>
  </div>);
}
