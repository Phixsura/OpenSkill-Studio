"use client";

interface Feature { icon: string; title: string; description: string; }
interface Stat { value: string; label: string; }
interface Testimonial { quote: string; author: string; role: string; }
interface LandingPageProps { heroTitle: string; heroSubtitle: string;
  ctaPrimary: { label: string; href: string }; ctaSecondary: { label: string; href: string };
  features: Feature[]; stats: Stat[]; testimonials: Testimonial[]; }

export function LandingPage({ heroTitle, heroSubtitle, ctaPrimary, ctaSecondary,
  features, stats, testimonials }: LandingPageProps) {
  return (
    <div className="space-y-16">
      <section className="py-20 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">{heroTitle}</h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-gray-500">{heroSubtitle}</p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <a href={ctaPrimary.href} className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-medium text-white shadow-lg">{ctaPrimary.label}</a>
          <a href={ctaSecondary.href} className="rounded-xl border px-6 py-3 text-sm font-medium dark:border-gray-700">{ctaSecondary.label}</a>
        </div>
      </section>
      <section className="flex justify-around py-8">
        {stats.map((s, i) => (
          <div key={i} className="text-center">
            <p className="text-3xl font-bold">{s.value}</p>
            <p className="text-sm text-gray-400">{s.label}</p>
          </div>
        ))}
      </section>
      <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {features.map(f => (
          <div key={f.title} className="rounded-xl border p-5 dark:border-gray-700">
            <span className="text-3xl">{f.icon}</span>
            <h3 className="mt-2 text-lg font-semibold">{f.title}</h3>
            <p className="mt-1 text-sm text-gray-500">{f.description}</p>
          </div>
        ))}
      </section>
      <section className="grid gap-4 sm:grid-cols-2">
        {testimonials.map((t, i) => (
          <div key={i} className="rounded-xl border p-5 dark:border-gray-700">
            <p className="text-sm italic">&ldquo;{t.quote}&rdquo;</p>
            <p className="mt-2 text-sm font-semibold">{t.author}</p>
            <p className="text-xs text-gray-400">{t.role}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
