"use client";

interface AnalyticsPageLayoutProps { appName: string; sections: string[]; activeSection: string; onSectionChange: (s: string) => void; children: React.ReactNode; }

const SECTION_ICONS: Record<string, string> = { installs: "📥", executions: "⚡", webhooks: "🔔", health: "❤️" };

export function AnalyticsPageLayout({ appName, sections, activeSection, onSectionChange, children }: AnalyticsPageLayoutProps) {
  return (
    <div>
      <h2 className="mb-4 text-xl font-bold">{appName} Analytics</h2>
      <div className="mb-6 flex gap-2 border-b border-gray-200 dark:border-gray-700">
        {sections.map(s => (
          <button key={s} onClick={() => onSectionChange(s)}
            className={`px-3 py-2 text-sm capitalize ${activeSection === s ? "border-b-2 border-blue-600 font-semibold text-blue-600" : "text-gray-500"}`}>
            {SECTION_ICONS[s] ?? "📊"} {s}
          </button>
        ))}
      </div>
      {children}
    </div>
  );
}
