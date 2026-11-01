"use client";
export function FleetKafkaPanel({ brokers, online, underReplicated, totalTopics, healthy }: { brokers: number; online: number; underReplicated: number; totalTopics: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📨 Kafka</h3>
    <div className="text-sm">{online}/{brokers} online · {totalTopics} topics</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {underReplicated} under-replicated partitions</span>}
  </div>);
}
