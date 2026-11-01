"use client";

interface StatBar { label: string; value: string; }
interface Feature { title: string; description: string; icon: string; }
interface Testimonial { quote: string; author: string; role: string; }
interface FooterSection { section: string; links: string[]; }
interface PlatformLandingPageProps {
  headline: string; subheadline: string; statsBar: StatBar[];
  features: Feature[]; testimonials: Testimonial[];
  footerLinks: FooterSection[]; onCta: (action: string) => void;
}

export function PlatformLandingPage({ headline, subheadline, statsBar, features,
  testimonials, footerLinks, onCta }: PlatformLandingPageProps) {
  return (
    <div className="space-y-16">
      {/* Hero */}
      <div className="rounded-2xl bg-gradient-to-br from-blue-600 via-purple-600 to-pink-500 px-8 py-16 text-center text-white">
        <h1 className="text-4xl font-black sm:text-5xl">{headline}</h1>
        <p className="mx-auto mt-4 max-w-xl text-lg opacity-80">{subheadline}</p>
        <div className="mt-8 flex justify-center gap-3">
          <button onClick={() => onCta("signup")} className="rounded-full bg-white px-8 py-3 font-bold text-blue-700 shadow-lg">
            Get Started Free
          </button>
          <button onClick={() => onCta("docs")} className="rounded-full border-2 border-white/30 px-8 py-3 font-medium">
            View Docs
          </button>
        </div>
        <div className="mt-10 flex justify-center gap-8">
          {statsBar.map(s => (
            <div key={s.label}>
              <p className="text-2xl font-black">{s.value}</p>
              <p className="text-xs opacity-60">{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div>
        <h2 className="text-center text-2xl font-bold">Why Developers Love Us</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map(f => (
            <div key={f.title} className="rounded-xl border p-6 dark:border-gray-700">
              <span className="text-3xl">{f.icon}</span>
              <h3 className="mt-3 text-lg font-bold">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-500">{f.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Testimonials */}
      {testimonials.length > 0 && (
        <div className="rounded-xl bg-gray-50 p-8 dark:bg-gray-800">
          <h2 className="text-center text-2xl font-bold">What Developers Say</h2>
          <div className="mt-6 grid gap-6 sm:grid-cols-3">
            {testimonials.map((t, i) => (
              <div key={i} className="rounded-lg bg-white p-5 shadow dark:bg-gray-900">
                <p className="text-sm italic text-gray-600 dark:text-gray-300">&ldquo;{t.quote}&rdquo;</p>
                <div className="mt-3">
                  <p className="text-sm font-bold">{t.author}</p>
                  <p className="text-xs text-gray-400">{t.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t pt-8 dark:border-gray-700">
        <div className="grid gap-6 sm:grid-cols-3">
          {footerLinks.map(sec => (
            <div key={sec.section}>
              <h4 className="text-sm font-bold">{sec.section}</h4>
              <ul className="mt-2 space-y-1">
                {sec.links.map(link => (
                  <li key={link} className="text-sm text-gray-400 hover:text-blue-500">{link}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <p className="mt-8 text-center text-xs text-gray-400">© 2026 OpenSkill. All rights reserved.</p>
      </footer>
    </div>
  );
}
