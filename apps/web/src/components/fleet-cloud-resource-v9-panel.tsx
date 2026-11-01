"use client";
export function FleetCloudResourceV9Panel({ resources, waste }: { resources: number; waste: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ Cloud Resource v9</h3>
    <div className="text-sm">{resources} resources · {waste} wasted</div>
  </div>);
}
