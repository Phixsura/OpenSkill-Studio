"use client";

interface Section { id: string; label: string; icon: string; count: number | null; href: string; }
interface Stat { label: string; value: number; display?: string; icon: string; }
interface DeveloperConsoleProps { greeting: string; sections: Section[]; stats: Stat[];
  orgName: string; orgPlan: string; notifications: number;
  onNavigate: (href: string) => void; }

export function DeveloperConsole({ greeting, sections, stats, orgName, orgPlan,
  notifications, onNavigate }: DeveloperConsoleProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{greeting}</h1>
          <p className="text-sm text-gray-400">{orgName} · <span className="capitalize">{orgPlan}</span></p>
        </div>
        {notifications > 0 && <span className="rounded-full bg-red-500 px-3 py-1 text-sm text-white">{notifications} 🔔</span>}
      </div>
      <div className="grid grid-cols-4 gap-3">
        {stats.map(s => (
          <div key={s.label} className="rounded-xl border p-4 text-center dark:border-gray-700">
            <span className="text-lg">{s.icon}</span>
            <p className="text-2xl font-bold mt-1">{s.display ?? s.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-4 gap-3">
        {sections.map(s => (
          <button key={s.id} onClick={() => onNavigate(s.href)}
            className="flex flex-col items-center gap-2 rounded-xl border p-4 transition hover:shadow-md dark:border-gray-700">
            <span className="text-2xl">{s.icon}</span>
            <span className="text-sm font-medium">{s.label}</span>
            {s.count != null && <span className="text-xs text-gray-400">{s.count}</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
