"use client";
export function FleetApiCompositionV9Panel({ compositions, backends }: { compositions: number; backends: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 API Composition v9</h3>
    <div className="text-sm">{compositions} compositions · {backends} backends</div>
  </div>);
}
