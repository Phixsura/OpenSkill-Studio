"use client";

interface AuditEntry { entryId: string; extensionId: string; actorId: string; action: string; details: string; timestamp: number; }

const actionIcons: Record<string, string> = {
  created: "🆕", published: "📢", updated: "🔄", unpublished: "📴", deleted: "🗑️",
  reviewed: "👀", approved: "✅", rejected: "❌", installed: "📥", uninstalled: "📤",
  permission_granted: "🔓", permission_revoked: "🔒", transferred: "🔀",
};

export function AuditTrailViewer({ entries }: { entries: AuditEntry[] }) {
  if (!entries.length) return <div className="text-center text-gray-400 py-6 text-sm">No audit events</div>;
  return (
    <div className="space-y-0.5">
      {entries.map((e, i) => (
        <div key={e.entryId} className="flex items-start gap-3 p-2 text-sm">
          <div className="flex flex-col items-center">
            <span>{actionIcons[e.action] || "📌"}</span>
            {i < entries.length - 1 && <div className="w-px h-6 bg-gray-200 dark:bg-gray-700 mt-1" />}
          </div>
          <div className="flex-1">
            <div className="flex justify-between">
              <span><span className="font-medium">{e.actorId}</span> <span className="text-gray-500">{e.action}</span></span>
              <span className="text-xs text-gray-400">{new Date(e.timestamp * 1000).toLocaleDateString()}</span>
            </div>
            {e.details && <p className="text-xs text-gray-500">{e.details}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}
