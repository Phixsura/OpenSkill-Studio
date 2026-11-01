"use client";
export function FleetApiGatewaySecurityV9Panel({ gateways, waf }: { gateways: number; waf: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 Gateway Security v9</h3>
    <div className="text-sm">{gateways} gateways · {waf} WAF enabled</div>
  </div>);
}
