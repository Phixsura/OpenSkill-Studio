"use client";

interface SocialProof { name: string; icon: string; value: string; }
interface LandingHeroProps { headline: string; subheadline: string;
  ctaPrimary: string; ctaSecondary: string;
  stats: Record<string, string>; socialProof: SocialProof[];
  onPrimary: () => void; onSecondary: () => void; }

export function LandingHero({ headline, subheadline, ctaPrimary, ctaSecondary,
  stats, socialProof, onPrimary, onSecondary }: LandingHeroProps) {
  return (
    <div className="text-center py-16">
      <h1 className="text-4xl sm:text-5xl font-black mb-4">{headline}</h1>
      <p className="text-lg text-gray-500 mb-8 max-w-2xl mx-auto">{subheadline}</p>
      <div className="flex gap-3 justify-center mb-10">
        <button onClick={onPrimary}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">{ctaPrimary}</button>
        <button onClick={onSecondary}
          className="px-6 py-3 border rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800">{ctaSecondary}</button>
      </div>
      <div className="flex justify-center gap-8 mb-8">
        {Object.entries(stats).map(([k, v]) => (
          <div key={k} className="text-center">
            <p className="text-2xl font-bold">{v}</p>
            <p className="text-xs text-gray-400 capitalize">{k.replace("_", " ")}</p>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-6 text-sm text-gray-400">
        {socialProof.map(s => (
          <span key={s.name} className="flex items-center gap-1">
            {s.icon} {s.value}
          </span>
        ))}
      </div>
    </div>
  );
}
