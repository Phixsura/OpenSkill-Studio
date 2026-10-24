"use client";

interface Feature { icon: string; title: string; desc: string; }
interface Testimonial { quote: string; author: string; rating: number; }
interface LandingPageSectionsProps { features: Feature[]; testimonials: Testimonial[];
  pricingTitle: string; pricingSubtitle: string; onGetStarted: () => void; }

export function LandingPageSections({ features, testimonials, pricingTitle, pricingSubtitle, onGetStarted }: LandingPageSectionsProps) {
  return (
    <div className="space-y-16">
      <section>
        <h2 className="text-2xl font-bold text-center mb-8">Everything You Need</h2>
        <div className="grid grid-cols-3 gap-6">
          {features.map(f => (
            <div key={f.title} className="text-center rounded-xl border dark:border-gray-700 p-6">
              <span className="text-3xl">{f.icon}</span>
              <h3 className="font-bold mt-2">{f.title}</h3>
              <p className="text-sm text-gray-500 mt-1">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
      <section className="text-center">
        <h2 className="text-2xl font-bold mb-6">Loved by Developers</h2>
        <div className="flex gap-6 justify-center">
          {testimonials.map((t, i) => (
            <div key={i} className="max-w-xs rounded-xl border dark:border-gray-700 p-5">
              <p className="text-yellow-500 mb-2">{"⭐".repeat(t.rating)}</p>
              <p className="text-sm italic text-gray-600 dark:text-gray-300">&ldquo;{t.quote}&rdquo;</p>
              <p className="text-xs text-gray-400 mt-2">— {t.author}</p>
            </div>
          ))}
        </div>
      </section>
      <section className="text-center rounded-2xl bg-blue-600 text-white p-10">
        <h2 className="text-2xl font-bold mb-2">{pricingTitle}</h2>
        <p className="text-sm opacity-90 mb-4">{pricingSubtitle}</p>
        <button onClick={onGetStarted}
          className="px-8 py-3 bg-white text-blue-600 rounded-xl font-medium hover:bg-gray-100">Get Started Free</button>
      </section>
    </div>
  );
}
