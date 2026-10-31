"use client";
export function FleetAmplifyPanel({ apps, deployed, backends, branches }: { apps: number; deployed: number; backends: number; branches: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔶 Amplify</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {backends} backends · {branches} branches</div>
  </div>);
}
