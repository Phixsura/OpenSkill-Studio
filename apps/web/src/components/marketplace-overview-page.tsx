"use client";

interface Section { title: string; type: string; count: number; }

interface MarketplaceOverviewPageProps { sections: Section[]; totalApps: number; totalDevelopers: number; }

export function MarketplaceOverviewPage({ sections, totalApps, totalDevelopers }: MarketplaceOverviewPageProps) {
  return (
    <div>
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-bold">OpenSkill Marketplace</h1>
        <p className="mt-2 text-gray-500">{totalApps} apps from {totalDevelopers} developers</p>
      </div>
      <div className="space-y-8">
        {sections.map(s => (
          <section key={s.type}>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-xl font-semibold">{s.title}</h2>
              <span className="text-sm text-gray-500">{s.count} apps</span>
            </div>
            <div className="rounded border border-dashed border-gray-300 p-8 text-center text-gray-400 dark:border-gray-700">
              {s.type} app grid
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
