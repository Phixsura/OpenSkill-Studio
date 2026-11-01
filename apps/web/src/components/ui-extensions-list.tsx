"use client";

interface Extension { surface: string; title: string; entryPath: string; }
interface UiExtensionsListProps { extensions: Extension[]; }

const SURFACE_ICONS: Record<string, string> = { dashboard_card: "📊", project_sidebar: "📋", settings_tab: "⚙️" };

export function UiExtensionsList({ extensions }: UiExtensionsListProps) {
  if (extensions.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No UI extensions</p>;
  return (
    <ul className="space-y-2">
      {extensions.map(e => (
        <li key={e.surface} className="flex items-center gap-2 rounded border border-gray-200 p-3 dark:border-gray-700">
          <span>{SURFACE_ICONS[e.surface] ?? "🧩"}</span>
          <div><span className="font-medium">{e.title}</span>
            <p className="text-xs text-gray-500">{e.surface} · {e.entryPath}</p></div>
        </li>
      ))}
    </ul>
  );
}
