"use client";

interface EndpointScope { endpoint: string; scopes: string[]; }
interface KeyPermissionsMatrixProps { endpoints: EndpointScope[];
  keyScopes: string[]; keyName: string; }

export function KeyPermissionsMatrix({ endpoints, keyScopes, keyName }: KeyPermissionsMatrixProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔐 Key Permissions</h3>
        <p className="text-xs text-gray-400">{keyName} · {keyScopes.length} scopes</p>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Endpoint</th><th className="p-3">Required</th><th className="p-3">Access</th>
        </tr></thead>
        <tbody>
          {endpoints.map(ep => {
            const hasAll = ep.scopes.every(s => keyScopes.includes(s));
            return (
              <tr key={ep.endpoint} className="border-b last:border-0 dark:border-gray-700">
                <td className="p-3 font-mono text-xs">{ep.endpoint}</td>
                <td className="p-3 text-center text-xs text-gray-400">{ep.scopes.join(", ")}</td>
                <td className="p-3 text-center">{hasAll ? "✅" : "❌"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
