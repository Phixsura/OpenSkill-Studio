"use client";
export function FleetStorageClassV9Panel({ classes, volumes }: { classes: number; volumes: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💾 Storage Class v9</h3>
    <div className="text-sm">{classes} classes · {volumes} volumes</div>
  </div>);
}
