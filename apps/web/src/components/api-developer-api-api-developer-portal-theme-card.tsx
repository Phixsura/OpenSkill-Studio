"use client";

interface ThemeInfo { primary_color: string; secondary_color: string; font_family: string; dark_mode: boolean; portal_title: string; has_custom: boolean; }
interface Props { theme: ThemeInfo; appName: string; }

export default function APIDeveloperAPIApiDeveloperPortalThemeCard({ theme, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎨 Portal Theme</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {theme.has_custom ? (
          <span className="rounded bg-purple-100 px-1.5 py-0.5 text-[9px] text-purple-700">custom</span>
        ) : (
          <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[9px] text-gray-500">default</span>
        )}
      </div>
      <div className="mb-3 text-center">
        <p className="text-[12px] font-bold text-gray-900 dark:text-gray-100">{theme.portal_title}</p>
      </div>
      <div className="flex items-center justify-center gap-3 mb-3">
        <div className="flex items-center gap-1.5">
          <div className="h-5 w-5 rounded" style={{ backgroundColor: theme.primary_color }} />
          <span className="font-mono text-[10px] text-gray-400">{theme.primary_color}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-5 w-5 rounded" style={{ backgroundColor: theme.secondary_color }} />
          <span className="font-mono text-[10px] text-gray-400">{theme.secondary_color}</span>
        </div>
      </div>
      <div className="flex justify-center gap-3 text-[10px] text-gray-400">
        <span>{theme.font_family}</span>
        <span>{theme.dark_mode ? "🌙 dark" : "☀️ light"}</span>
      </div>
    </div>
  );
}
