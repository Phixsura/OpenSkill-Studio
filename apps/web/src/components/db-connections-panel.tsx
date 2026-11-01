"use client";

interface DbConn { connId: string; dbType: string; host: string; database: string; status: string; poolSize: number; activeQueries: number; totalQueries: number; }

const dbIcons: Record<string, string> = { postgres: "🐘", mysql: "🐬", sqlite: "📁", redis: "🔴", mongodb: "🍃" };

export function DbConnectionsPanel({ connections, onDisconnect }: {
  connections: DbConn[]; onDisconnect?: (connId: string) => void;
}) {
  if (!connections.length) return <div className="text-center text-gray-400 py-6 text-sm">No database connections</div>;
  return (
    <div className="space-y-2">
      {connections.map(c => (
        <div key={c.connId} className={`border rounded-xl p-3 ${c.status === "connected" ? "border-green-200 dark:border-gray-700" : "border-red-200 dark:border-red-800 opacity-60"}`}>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-xl">{dbIcons[c.dbType] || "🗄️"}</span>
              <div>
                <span className="font-medium text-sm">{c.database}</span>
                <span className="text-xs text-gray-500 ml-1">({c.dbType})</span>
                <span className="text-xs text-gray-400 block">{c.host}</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs"><span className="font-medium">{c.activeQueries}</span>/{c.poolSize} pool</div>
              <span className="text-[10px] text-gray-400">{c.totalQueries} total queries</span>
            </div>
          </div>
          {c.status === "connected" && (
            <button onClick={() => onDisconnect?.(c.connId)} className="text-xs text-red-400 mt-1">Disconnect</button>
          )}
        </div>
      ))}
    </div>
  );
}
