"use client";

interface Section { key: string; title: string; type: string; }
interface StatsBar { apps: number; developers: number; installs: number; }
interface MarketplaceHomepageLayoutProps { sections: Section[]; statsBar: StatsBar; personalized: boolean; }

export function MarketplaceHomepageLayout({ sections, statsBar, personalized }: MarketplaceHomepageLayoutProps) {
  return (
    <div className="space-y-8">
      {/* Stats bar */}
      <div className="flex justify-center gap-8 rounded-lg bg-gray-50 py-3 dark:bg-gray-800">
        <span className="text-sm"><strong>{statsBar.apps.toLocaleString()}</strong> apps</span>
        <span className="text-sm"><strong>{statsBar.developers.toLocaleString()}</strong> developers</span>
        <span className="text-sm"><strong>{statsBar.installs.toLocaleString()}</strong> installs</span>
      </div>
      {personalized && (
        <p className="text-center text-xs text-blue-600">✨ Personalized for you</p>
      )}
      {/* Section placeholders */}
      {sections.map(s => (
        <section key={s.key}>
          <h2 className="mb-3 text-xl font-bold">{s.title}</h2>
          <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center text-sm text-gray-400 dark:border-gray-700">
            [{s.type}] — {s.title}
          </div>
        </section>
      ))}
    </div>
  );
}
