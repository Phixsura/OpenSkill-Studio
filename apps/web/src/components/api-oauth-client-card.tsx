"use client";

interface OAuthClientInfo {
  client_id: string;
  client_name: string;
  grant_types: string[];
  redirect_uri_count: number;
  active: boolean;
}

interface APIOAuthClientCardProps {
  clients: OAuthClientInfo[];
  appName: string;
}

export default function APIOAuthClientCard({ clients, appName }: APIOAuthClientCardProps) {
  const active = clients.filter((c) => c.active).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 OAuth Clients</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active}/{clients.length} active</span>
      </div>

      {clients.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No OAuth clients</p>
      ) : (
        <div className="space-y-2">
          {clients.map((c) => (
            <div key={c.client_id} className={`rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800 ${!c.active ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{c.client_name}</span>
                <span className="font-mono text-[10px] text-gray-400">{c.client_id.slice(0, 12)}...</span>
              </div>
              <div className="mt-1 flex flex-wrap gap-1">
                {c.grant_types.map((g) => (
                  <span key={g} className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{g}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
