"use client";
export function FleetAiMultiCloudV2Panel({ managers, active, clouds, deployments, failover }: { managers: number; active: number; clouds: string[]; deployments: number; failover: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☁️ AI Multi-Cloud v2</h3>
    <div className="text-sm">{active}/{managers} active · {clouds.join(", ")} · {deployments} deploys · {failover ? "✅" : "⚠️"} failover</div>
  </div>);
}
