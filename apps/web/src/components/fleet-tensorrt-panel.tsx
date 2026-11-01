"use client";
export function FleetTensorrtPanel({ engines, active, throughput, p99 }: { engines: number; active: number; throughput: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 TensorRT</h3>
    <div className="text-sm">{active}/{engines} active · {throughput.toLocaleString()} inf/s · p99 {p99}ms</div>
  </div>);
}
