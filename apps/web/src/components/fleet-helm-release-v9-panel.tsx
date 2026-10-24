"use client";
export function FleetHelmReleaseV9Panel({ releases, deployed }: { releases: number; deployed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⎈ Helm Release v9</h3>
    <div className="text-sm">{releases} releases · {deployed} deployed</div>
  </div>);
}
