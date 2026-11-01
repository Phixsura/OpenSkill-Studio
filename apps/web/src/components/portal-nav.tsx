"use client";

interface PortalNavProps { activeSection: string; }

const NAV_ITEMS = [
  { key: "overview", label: "Overview", icon: "🏠" },
  { key: "apps", label: "My Apps", icon: "📦" },
  { key: "keys", label: "API Keys", icon: "🔑" },
  { key: "webhooks", label: "Webhooks", icon: "🔔" },
  { key: "analytics", label: "Analytics", icon: "📊" },
  { key: "settings", label: "Settings", icon: "⚙️" },
  { key: "docs", label: "Documentation", icon: "📖" },
];

export function PortalNav({ activeSection }: PortalNavProps) {
  return (
    <nav className="space-y-1">
      {NAV_ITEMS.map(item => (
        <a key={item.key} href={`/dashboard/developer/${item.key === "overview" ? "" : item.key}`}
          className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
            activeSection === item.key ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-900/20" : "text-gray-600 hover:bg-gray-100 dark:text-gray-400"
          }`}>
          <span>{item.icon}</span>{item.label}
        </a>
      ))}
    </nav>
  );
}
