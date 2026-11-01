"use client";
export function FleetMlModelRegistryV9Panel({ models, deployed }: { models: number; deployed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤖 ML Model Registry v9</h3>
    <div className="text-sm">{models} models · {deployed} deployed</div>
  </div>);
}
