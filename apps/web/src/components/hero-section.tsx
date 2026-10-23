"use client";

interface Stat { label: string; value: string; }
interface HeroSectionProps { headline: string; subheadline: string; ctaPrimary: string;
  ctaSecondary: string | null; stats: Stat[]; gradient: string;
  onCtaPrimary: () => void; onCtaSecondary?: () => void; }

export function HeroSection({ headline, subheadline, ctaPrimary, ctaSecondary,
  stats, gradient, onCtaPrimary, onCtaSecondary }: HeroSectionProps) {
  return (
    <div className={`rounded-2xl bg-gradient-to-r ${gradient} px-8 py-14 text-center text-white`}>
      <h1 className="text-4xl font-black sm:text-5xl">{headline}</h1>
      <p className="mx-auto mt-4 max-w-lg text-lg opacity-80">{subheadline}</p>
      <div className="mt-8 flex justify-center gap-3">
        <button onClick={onCtaPrimary}
          className="rounded-full bg-white px-8 py-3 font-bold text-blue-700 shadow-lg">
          {ctaPrimary}
        </button>
        {ctaSecondary && onCtaSecondary && (
          <button onClick={onCtaSecondary}
            className="rounded-full border-2 border-white/30 px-8 py-3 font-medium">
            {ctaSecondary}
          </button>
        )}
      </div>
      {stats.length > 0 && (
        <div className="mt-10 flex justify-center gap-8">
          {stats.map(s => (
            <div key={s.label}>
              <p className="text-2xl font-black">{s.value}</p>
              <p className="text-xs opacity-60">{s.label}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
