"use client";
export function FleetRdsPanel({ instances, available, multiAz, storageGb }: { instances: number; available: number; multiAz: number; storageGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗄️ RDS</h3>
    <div className="text-sm">{available}/{instances} available · {multiAz} multi-AZ · {storageGb}GB</div>
  </div>);
}
