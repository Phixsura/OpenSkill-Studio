"use client";

interface Stat { label: string; value: string; icon: string; }
interface Feature { title: string; description: string; icon: string; }
interface FinalHeroPageProps { headline: string; subheadline: string;
  stats: Stat[]; features: Feature[];
  ctaPrimary: string; ctaSecondary: string;
  trustRating: string; trustInstalls: string;
  onPrimary: () => void; onSecondary: () => void; }

export function FinalHeroPage({ headline, subheadline, stats, features,
  ctaPrimary, ctaSecondary, trustRating, trustInstalls, onPrimary, onSecondary }: FinalHeroPageProps) {
  return (
    <div className="space-y-12 py-12">
      <div className="text-center max-w-3xl mx-auto">
        <h1 className="text-4xl sm:text-5xl font-black mb-4">{headline}</h1>
        <p className="text-lg text-gray-500 mb-8">{subheadline}</p>
        <div className="flex gap-3 justify-center mb-6">
          <button onClick={onPrimary} className="px-8 py-3 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700">{ctaPrimary}</button>
          <button onClick={onSecondary} className="px-8 py-3 border rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800">{ctaSecondary}</button>
        </div>
        <div className="flex justify-center gap-2 text-xs text-gray-400">
          <span>{trustRating}</span><span>·</span><span>{trustInstalls} installs</span>
        </div>
      </div>
      <div className="flex justify-center gap-8">
        {stats.map(s => (
          <div key={s.label} className="text-center">
            <p className="text-lg">{s.icon}</p>
            <p className="text-2xl font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-4 max-w-3xl mx-auto">
        {features.map(f => (
          <div key={f.title} className="rounded-xl border dark:border-gray-700 p-4 text-center">
            <p className="text-2xl mb-1">{f.icon}</p>
            <h3 className="text-sm font-bold">{f.title}</h3>
            <p className="text-xs text-gray-500">{f.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
