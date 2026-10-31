"use client";

interface Client { clientId: string; name: string; redirectUris: string[]; scopes: string[]; active: boolean; createdAt: string; }
interface Props { clients: Client[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClientCard({ clients, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 OAuth Clients</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {clients.length} clients</p>
      </div>
      {clients.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No OAuth clients</p>
      ) : (
        <div className="space-y-2">
          {clients.map((c) => (
            <div key={c.clientId} className={`rounded-lg bg-gray-50 p-2 dark:bg-gray-800 ${!c.active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{c.name}</span>
                <span className={c.active ? "text-green-500" : "text-red-400"}>{c.active ? "Active" : "Revoked"}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                <code>{c.clientId}</code> · {c.redirectUris.length} redirect URIs
              </div>
              {c.scopes.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">{c.scopes.map((s) => <span key={s} className="rounded bg-blue-100 px-1 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{s}</span>)}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
