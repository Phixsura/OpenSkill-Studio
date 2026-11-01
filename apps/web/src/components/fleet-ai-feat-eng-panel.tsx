"use client";
export function FleetAiFeatEngPanel({ engines, active, features, transforms, impact }: { engines: number; active: number; features: number; transforms: number; impact: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Feature Engineering</h3>
    <div className="text-sm">{active}/{engines} active · {features} features · {transforms.toLocaleString()} transforms · +{impact}% impact</div>
  </div>);
}
