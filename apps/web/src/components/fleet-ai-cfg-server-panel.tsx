"use client";
export function FleetAiCfgServerPanel({ servers, active, configs, clients, updates }: { servers: number; active: number; configs: number; clients: number; updates: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ AI Config Server</h3>
    <div className="text-sm">{active}/{servers} active · {configs} configs · {clients} clients · {updates} updates</div>
  </div>);
}
