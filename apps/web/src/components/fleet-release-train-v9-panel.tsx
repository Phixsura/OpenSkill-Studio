"use client";
export function FleetReleaseTrainV9Panel({ releases, avgLead }: { releases: number; avgLead: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚂 Release Train v9</h3>
    <div className="text-sm">{releases} releases · {avgLead}h avg lead</div>
  </div>);
}
