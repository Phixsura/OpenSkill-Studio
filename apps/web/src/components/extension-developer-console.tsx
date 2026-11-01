"use client";

import { useState } from "react";

interface ConsoleSection {
  id: string;
  label: string;
  icon: string;
  count?: number;
  status?: "ok" | "warning" | "error";
}

interface QuickStat {
  label: string;
  value: string | number;
  trend?: "up" | "down" | "flat";
}

export function ExtensionDeveloperConsole({
  extensionName,
  version,
  sections,
  quickStats,
  onNavigate,
}: {
  extensionName: string;
  version: string;
  sections: ConsoleSection[];
  quickStats: QuickStat[];
  onNavigate?: (sectionId: string) => void;
}) {
  const [activeSection, setActiveSection] = useState<string | null>(null);

  const trendIcons: Record<string, string> = { up: "📈", down: "📉", flat: "➡️" };
  const statusColors: Record<string, string> = {
    ok: "bg-green-500", warning: "bg-yellow-500", error: "bg-red-500",
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold">🖥️ Developer Console</h2>
          <span className="font-semibold">{extensionName}</span>
          <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">v{version}</code>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {quickStats.map((stat) => (
          <div key={stat.label} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <span className="text-xs text-gray-500 block">{stat.label}</span>
            <div className="flex items-center justify-center gap-1">
              <span className="text-lg font-bold">{stat.value}</span>
              {stat.trend && <span className="text-xs">{trendIcons[stat.trend]}</span>}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {sections.map((section) => (
          <button key={section.id}
            onClick={() => { setActiveSection(section.id); onNavigate?.(section.id); }}
            className={`rounded-xl border dark:border-gray-700 p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition ${
              activeSection === section.id ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/10" : ""
            }`}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xl">{section.icon}</span>
              {section.status && (
                <span className={`w-2.5 h-2.5 rounded-full ${statusColors[section.status]}`} />
              )}
            </div>
            <span className="font-semibold text-sm block">{section.label}</span>
            {section.count !== undefined && (
              <span className="text-xs text-gray-400">{section.count} items</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
