"use client";
export function FleetStreamProcessorV9Panel({ streams, throughput }: { streams: number; throughput: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌊 Stream Processor v9</h3>
    <div className="text-sm">{streams} streams · {throughput.toLocaleString()} events/s</div>
  </div>);
}
