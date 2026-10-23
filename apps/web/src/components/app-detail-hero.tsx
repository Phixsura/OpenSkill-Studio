"use client";

interface Badge { label: string; icon?: string; }
interface AppDetailHeroProps {
  appName: string; shortDescription: string; category: string; priceLabel: string;
  developerName: string; developerVerified: boolean;
  installs: number; rating: number; reviews: number; version: string;
  badges: Badge[]; ctaLabel: string; ctaDisabled: boolean; onCta: () => void;
}

export function AppDetailHero({ appName, shortDescription, category, priceLabel, developerName, developerVerified,
  installs, rating, reviews, version, badges, ctaLabel, ctaDisabled, onCta }: AppDetailHeroProps) {
  return (
    <div className="rounded-xl bg-gradient-to-r from-gray-50 to-blue-50 p-6 dark:from-gray-800 dark:to-blue-900/20">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">{appName}</h1>
            <span className="rounded bg-gray-200 px-2 py-0.5 text-xs dark:bg-gray-700">{priceLabel}</span>
          </div>
          <p className="mt-1 text-sm text-gray-500">{shortDescription}</p>
          <div className="mt-2 flex items-center gap-2 text-sm text-gray-400">
            <span>{developerName} {developerVerified && "✅"}</span>
            <span>·</span>
            <span>{category}</span>
            <span>·</span>
            <span>v{version}</span>
          </div>
        </div>
        <button onClick={onCta} disabled={ctaDisabled}
          className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50">
          {ctaLabel}
        </button>
      </div>
      <div className="mt-4 flex items-center gap-6 text-sm">
        <span>📥 {installs.toLocaleString()} installs</span>
        <span>⭐ {rating.toFixed(1)} ({reviews} reviews)</span>
        {badges.map((b, i) => (
          <span key={i} className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">
            {b.icon || "🏅"} {b.label}
          </span>
        ))}
      </div>
    </div>
  );
}
