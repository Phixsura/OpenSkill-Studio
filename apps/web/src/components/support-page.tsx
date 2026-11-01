"use client";

interface Resource { id: string; title: string; icon: string; href: string; description: string; }
interface SupportPageProps { resources: Resource[]; openTickets: number;
  recentIncidents: number; hasAlerts: boolean; onNavigate: (href: string) => void; }

export function SupportPage({ resources, openTickets, recentIncidents, hasAlerts, onNavigate }: SupportPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">🛟 Help & Support</h1>
      {hasAlerts && (
        <div className="flex gap-3">
          {openTickets > 0 && (
            <div className="flex-1 rounded-lg bg-blue-50 px-4 py-3 dark:bg-blue-900/10">
              <p className="text-sm"><strong>{openTickets}</strong> open ticket{openTickets !== 1 ? "s" : ""}</p>
            </div>
          )}
          {recentIncidents > 0 && (
            <div className="flex-1 rounded-lg bg-yellow-50 px-4 py-3 dark:bg-yellow-900/10">
              <p className="text-sm">⚠ <strong>{recentIncidents}</strong> active incident{recentIncidents !== 1 ? "s" : ""}</p>
            </div>
          )}
        </div>
      )}
      <div className="grid gap-3 sm:grid-cols-2">
        {resources.map(r => (
          <button key={r.id} onClick={() => onNavigate(r.href)}
            className="flex items-start gap-3 rounded-xl border p-4 text-left hover:shadow dark:border-gray-700">
            <span className="text-2xl">{r.icon}</span>
            <div>
              <p className="text-sm font-semibold">{r.title}</p>
              <p className="text-xs text-gray-400 mt-0.5">{r.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
