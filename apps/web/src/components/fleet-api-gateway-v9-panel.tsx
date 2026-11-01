"use client";
export function FleetApiGatewayV9Panel({ routes, rps }: { routes: number; rps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 API Gateway v9</h3>
    <div className="text-sm">{routes} routes · {rps.toLocaleString()} rps</div>
  </div>);
}
