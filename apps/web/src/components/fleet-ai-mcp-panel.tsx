"use client";
export function FleetAiMcpPanel({ servers, running, tools, resources, calls }: { servers: number; running: number; tools: number; resources: number; calls: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 AI MCP</h3>
    <div className="text-sm">{running}/{servers} running · {tools} tools · {resources} resources · {calls.toLocaleString()} calls</div>
  </div>);
}
