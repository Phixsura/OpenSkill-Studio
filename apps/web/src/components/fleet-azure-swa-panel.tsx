"use client";
export function FleetAzureSwaPanel({ apps, deployed, apiFunctions, customDomains }: { apps: number; deployed: number; apiFunctions: number; customDomains: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Azure SWA</h3>
    <div className="text-sm">{deployed}/{apps} deployed · {apiFunctions} APIs · {customDomains} domains</div>
  </div>);
}
