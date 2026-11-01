"use client";
export function FleetEksPanel({ clusters, active, fargateProfiles, managedNodegroups }: { clusters: number; active: number; fargateProfiles: number; managedNodegroups: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ EKS</h3>
    <div className="text-sm">{active}/{clusters} active · {fargateProfiles} Fargate · {managedNodegroups} managed</div>
  </div>);
}
