"use client";
export function FleetApiWebsocketAuthV9Panel({ connections, authenticated }: { connections: number; authenticated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 WS Auth v9</h3>
    <div className="text-sm">{connections} connections · {authenticated} authenticated</div>
  </div>);
}
