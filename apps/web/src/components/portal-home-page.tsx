"use client";

interface StatItem { icon: string; value: string; label: string; }
interface QuickLink { label: string; icon: string; path: string; }
interface PortalHomePageProps { greeting: string; statsBar: StatItem[];
  quickLinks: QuickLink[]; onNavigate: (path: string) => void; }

export function PortalHomePage({ greeting, statsBar, quickLinks, onNavigate }: PortalHomePageProps) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{greeting}</h1>
      <div className="flex gap-4 overflow-x-auto">
        {statsBar.map(s => (
          <div key={s.label} className="shrink-0 rounded-xl border dark:border-gray-700 px-4 py-3 text-center min-w-[100px]">
            <p className="text-lg">{s.icon}</p>
            <p className="text-lg font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div>
        <h2 className="text-sm font-semibold mb-2">⚡ Quick Links</h2>
        <div className="flex gap-2">
          {quickLinks.map(l => (
            <button key={l.path} onClick={() => onNavigate(l.path)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-800 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
              <span>{l.icon}</span>{l.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
