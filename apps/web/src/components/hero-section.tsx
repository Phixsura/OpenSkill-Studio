"use client";

interface HeroStat { value: string; label: string; }
interface Cta { label: string; href: string; }
interface HeroSectionProps { title: string; subtitle: string; badge: string | null;
  ctaPrimary: Cta; ctaSecondary: Cta | null; stats: HeroStat[]; }

export function HeroSection({ title, subtitle, badge, ctaPrimary, ctaSecondary, stats }: HeroSectionProps) {
  return (
    <div className="py-16 text-center">
      {badge && (
        <span className="mb-4 inline-block rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">{badge}</span>
      )}
      <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">{title}</h1>
      <p className="mx-auto mt-4 max-w-xl text-lg text-gray-500">{subtitle}</p>
      <div className="mt-8 flex items-center justify-center gap-3">
        <a href={ctaPrimary.href} className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white shadow-lg hover:bg-blue-700">{ctaPrimary.label}</a>
        {ctaSecondary && (
          <a href={ctaSecondary.href} className="rounded-lg border px-6 py-3 text-sm font-medium dark:border-gray-700">{ctaSecondary.label}</a>
        )}
      </div>
      {stats.length > 0 && (
        <div className="mt-12 flex items-center justify-center gap-8">
          {stats.map((s, i) => (
            <div key={i} className="text-center">
              <p className="text-2xl font-bold">{s.value}</p>
              <p className="text-xs text-gray-400">{s.label}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
