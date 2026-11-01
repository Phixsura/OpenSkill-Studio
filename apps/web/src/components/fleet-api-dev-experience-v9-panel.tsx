"use client";
export function FleetApiDevExperienceV9Panel({ metrics, satisfaction }: { metrics: number; satisfaction: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💻 API DevX v9</h3>
    <div className="text-sm">{metrics} metrics · {satisfaction}/100 satisfaction</div>
  </div>);
}
