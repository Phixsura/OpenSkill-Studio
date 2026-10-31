"use client";
const cfg: Record<string, { color: string; icon: string }> = {
  draft: { color: "bg-gray-100 text-gray-600", icon: "📝" },
  review: { color: "bg-blue-100 text-blue-700", icon: "🔍" },
  active: { color: "bg-green-100 text-green-700", icon: "✅" },
  suspended: { color: "bg-red-100 text-red-600", icon: "⛔" },
  archived: { color: "bg-gray-200 text-gray-500", icon: "📦" },
};
export function ExtensionStatusBadge({ status }: { status: string }) {
  const c = cfg[status] || cfg.draft;
  return <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${c.color}`}>{c.icon} {status}</span>;
}
