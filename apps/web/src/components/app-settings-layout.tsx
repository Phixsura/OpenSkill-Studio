"use client";

interface SettingsSection { id: string; title: string; icon: string; fields: string[]; }
interface AppSettingsLayoutProps { appName: string; sections: SettingsSection[];
  activeSection: string; onSelectSection: (id: string) => void; children: React.ReactNode; }

export function AppSettingsLayout({ appName, sections, activeSection, onSelectSection, children }: AppSettingsLayoutProps) {
  return (
    <div>
      <h1 className="text-xl font-bold mb-5">{appName} Settings</h1>
      <div className="flex gap-6">
        <nav className="w-48 shrink-0 space-y-1">
          {sections.map(s => (
            <button key={s.id} onClick={() => onSelectSection(s.id)}
              className={`w-full text-left flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
                s.id === activeSection ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 font-medium" :
                s.id === "danger" ? "text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10" :
                "text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800"
              }`}>{s.icon} {s.title}</button>
          ))}
        </nav>
        <div className="flex-1">{children}</div>
      </div>
    </div>
  );
}
