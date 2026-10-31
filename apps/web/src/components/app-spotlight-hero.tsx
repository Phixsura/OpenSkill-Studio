"use client";

interface AppSpotlightHeroProps { appName: string; category: string; rating: number;
  installCount: number; curatorNote: string; highlights: string[];
  week: string; onInstall: () => void; onLearnMore: () => void; }

export function AppSpotlightHero({ appName, category, rating, installCount,
  curatorNote, highlights, week, onInstall, onLearnMore }: AppSpotlightHeroProps) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
      <p className="text-xs opacity-60">🌟 App of the Week — {week}</p>
      <h2 className="mt-2 text-2xl font-black">{appName}</h2>
      <p className="mt-1 text-sm opacity-80">{curatorNote}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {highlights.map((h, i) => (
          <span key={i} className="rounded-full bg-white/15 px-3 py-1 text-xs">{h}</span>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        <button onClick={onInstall} className="rounded-lg bg-white px-5 py-2 text-sm font-bold text-indigo-700">
          Install Free
        </button>
        <button onClick={onLearnMore} className="rounded-lg border border-white/30 px-5 py-2 text-sm">
          Learn More
        </button>
      </div>
    </div>
  );
}
