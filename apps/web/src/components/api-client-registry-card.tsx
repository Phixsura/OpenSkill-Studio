"use client";

interface ClientInfo {
  client_id: string;
  name: string;
  status: "active" | "suspended" | "revoked";
  request_count: number;
}

interface APIClientRegistryCardProps {
  clients: ClientInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  suspended: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  revoked: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function APIClientRegistryCard({ clients, appName }: APIClientRegistryCardProps) {
  const active = clients.filter((c) => c.status === "active").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">👥 API Clients</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active}/{clients.length} active</span>
      </div>

      {clients.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No registered clients</p>
      ) : (
        <div className="space-y-1.5">
          {clients.map((c) => (
            <div key={c.client_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-800 dark:text-gray-200">{c.name}</span>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[c.status]}`}>{c.status}</span>
              </div>
              <span className="text-[10px] text-gray-400">{c.request_count} reqs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
