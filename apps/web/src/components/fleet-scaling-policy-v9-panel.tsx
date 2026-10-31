"use client";
export function FleetScalingPolicyV9Panel({ policies, scaleUps }: { policies: number; scaleUps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Scaling Policy v9</h3>
    <div className="text-sm">{policies} policies · {scaleUps} scale-ups today</div>
  </div>);
}
