"use client";

interface Testimonial { quote: string; author: string; role: string; company: string; }
interface SocialProofSectionProps { testimonials: Testimonial[];
  stats: Record<string, string>; }

export function SocialProofSection({ testimonials, stats }: SocialProofSectionProps) {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-around py-6">
        {Object.entries(stats).map(([k, v]) => (
          <div key={k} className="text-center">
            <p className="text-2xl font-bold">{v}</p>
            <p className="text-xs text-gray-400 capitalize">{k}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {testimonials.map((t, i) => (
          <div key={i} className="rounded-xl border p-4 dark:border-gray-700">
            <p className="text-sm italic text-gray-600 dark:text-gray-300">&ldquo;{t.quote}&rdquo;</p>
            <div className="mt-3">
              <p className="text-sm font-semibold">{t.author}</p>
              <p className="text-xs text-gray-400">{t.role} at {t.company}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
