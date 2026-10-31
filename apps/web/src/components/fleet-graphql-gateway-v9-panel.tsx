"use client";
export function FleetGraphqlGatewayV9Panel({ endpoints, qps }: { endpoints: number; qps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">◈ GraphQL Gateway v9</h3>
    <div className="text-sm">{endpoints} endpoints · {qps.toLocaleString()} qps</div>
  </div>);
}
