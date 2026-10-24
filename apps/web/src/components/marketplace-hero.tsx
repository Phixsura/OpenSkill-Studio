"use client";

interface MarketplaceHeroProps { tagline: string; totalApps: number; totalDevelopers: number; }

export function MarketplaceHero({ tagline, totalApps, totalDevelopers }: MarketplaceHeroProps) {
  return (
    <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 p-8 text-center text-white">
      <h1 className="text-3xl font-bold">{tagline}</h1>
      <p className="mt-2 text-lg opacity-80">{totalApps} apps from {totalDevelopers} developers</p>
      <div className="mt-6 flex justify-center gap-4">
        <a href="/marketplace/apps" className="rounded-lg bg-white px-6 py-2.5 font-medium text-blue-600">Explore Apps</a>
        <a href="/dashboard/developer" className="rounded-lg border border-white px-6 py-2.5 font-medium">Build an App</a>
      </div>
    </div>
  );
}
