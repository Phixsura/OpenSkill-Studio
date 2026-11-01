"use client";
export function FleetApiGrpcGatewayV9Panel({ gateways, methods }: { gateways: number; methods: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ gRPC Gateway v9</h3>
    <div className="text-sm">{gateways} gateways · {methods} methods</div>
  </div>);
}
