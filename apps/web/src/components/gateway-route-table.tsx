"use client";

interface Route { path_pattern: string; target_app_id: string; methods: string[]; auth_required: boolean; rate_limit: number; }
interface GatewayRouteTableProps { routes: Route[]; }

export function GatewayRouteTable({ routes }: GatewayRouteTableProps) {
  if (routes.length === 0) return <p className="text-sm text-gray-400">No routes configured.</p>;
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-4 py-2 text-left">Path</th>
            <th className="px-4 py-2 text-left">Methods</th>
            <th className="px-4 py-2 text-left">Target</th>
            <th className="px-4 py-2 text-center">Auth</th>
            <th className="px-4 py-2 text-right">Rate Limit</th>
          </tr>
        </thead>
        <tbody>
          {routes.map((r, i) => (
            <tr key={i} className="border-t dark:border-gray-700">
              <td className="px-4 py-2 font-mono text-xs">{r.path_pattern}</td>
              <td className="px-4 py-2">{r.methods.map(m => (
                <span key={m} className="mr-1 rounded bg-blue-100 px-1 py-0.5 text-xs text-blue-700">{m}</span>
              ))}</td>
              <td className="px-4 py-2 font-mono text-xs">{r.target_app_id}</td>
              <td className="px-4 py-2 text-center">{r.auth_required ? "🔒" : "🔓"}</td>
              <td className="px-4 py-2 text-right text-xs text-gray-400">{r.rate_limit}/min</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
