"use client";

interface GatewayRoute { path: string; upstream: string; methods: string[];
  rateLimit: number; authRequired: boolean; enabled: boolean; }
interface GatewayRoutesTableProps { routes: GatewayRoute[]; middleware: string[];
  onToggle: (path: string) => void; }

export function GatewayRoutesTable({ routes, middleware, onToggle }: GatewayRoutesTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚪 API Gateway</h3>
        <span className="text-xs text-gray-400">{routes.length} routes · {middleware.length} middleware</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Path</th><th className="p-3 text-left">Upstream</th>
          <th className="p-3">Auth</th><th className="p-3">Rate</th><th className="p-3">Active</th>
        </tr></thead>
        <tbody>
          {routes.map(r => (
            <tr key={r.path} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-mono text-xs">{r.path}</td>
              <td className="p-3 text-xs text-gray-400">{r.upstream}</td>
              <td className="p-3 text-center">{r.authRequired ? "🔒" : "🔓"}</td>
              <td className="p-3 text-center text-xs">{r.rateLimit || "—"}</td>
              <td className="p-3 text-center">
                <button onClick={() => onToggle(r.path)}
                  className={`w-8 h-4 rounded-full ${r.enabled ? "bg-green-500" : "bg-gray-300"}`}>
                  <span className={`block w-3 h-3 rounded-full bg-white transform ${r.enabled ? "translate-x-4" : "translate-x-0.5"}`} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
