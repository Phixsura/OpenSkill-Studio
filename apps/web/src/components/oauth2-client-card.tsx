"use client";

interface OAuth2Client { clientId: string; name: string; scopes: string[]; active: boolean; }
interface OAuth2ClientCardProps { clients: OAuth2Client[]; onRevoke: (clientId: string) => void; }

export function OAuth2ClientCard({ clients, onRevoke }: OAuth2ClientCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔑 OAuth2 Clients</h3>
      <div className="space-y-3">
        {clients.map(c => (
          <div key={c.clientId} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3">
            <div>
              <p className="text-sm font-medium">{c.name}</p>
              <p className="text-xs font-mono text-gray-400">{c.clientId}</p>
              <div className="flex gap-1 mt-1">
                {c.scopes.map(s => (
                  <span key={s} className="text-xs bg-blue-50 dark:bg-blue-900/20 text-blue-600 px-1.5 py-0.5 rounded">{s}</span>
                ))}
              </div>
            </div>
            {c.active
              ? <button onClick={() => onRevoke(c.clientId)}
                  className="text-xs px-2 py-1 border border-red-200 text-red-600 rounded hover:bg-red-50">Revoke</button>
              : <span className="text-xs text-gray-400">Revoked</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
