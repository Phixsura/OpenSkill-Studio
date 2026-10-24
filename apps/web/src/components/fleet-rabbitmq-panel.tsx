"use client";
export function FleetRabbitmqPanel({ nodes, running, queues, messages, healthy }: { nodes: number; running: number; queues: number; messages: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐰 RabbitMQ</h3>
    <div className="text-sm">{running}/{nodes} running · {queues} queues · {messages.toLocaleString()} msgs</div>
  </div>);
}
