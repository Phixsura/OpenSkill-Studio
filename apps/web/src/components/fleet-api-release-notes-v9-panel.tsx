"use client";
export function FleetApiReleaseNotesV9Panel({ releases, features }: { releases: number; features: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 Release Notes v9</h3>
    <div className="text-sm">{releases} releases · {features} features</div>
  </div>);
}
