"use client";
export function FleetQueueBrokerV9Panel({ queues, throughput }: { queues: number; throughput: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📨 Queue Broker v9</h3>
    <div className="text-sm">{queues} queues · {throughput.toLocaleString()} msg/s</div>
  </div>);
}
