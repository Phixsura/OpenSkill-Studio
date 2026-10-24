"use client";
export function FleetGrpcHealthV9Panel({ services, serving }: { services: number; serving: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ gRPC Health v9</h3>
    <div className="text-sm">{services} services · {serving} serving</div>
  </div>);
}
