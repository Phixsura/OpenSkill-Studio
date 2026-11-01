"use client";

interface FeaturedBannerProps { title: string; subtitle: string; ctaLabel: string;
  ctaHref: string; backgroundColor: string; icon: string; onDismiss: () => void; }

export function FeaturedBanner({ title, subtitle, ctaLabel, ctaHref, backgroundColor, icon, onDismiss }: FeaturedBannerProps) {
  return (
    <div className="relative overflow-hidden rounded-xl p-5 text-white" style={{ backgroundColor }}>
      <button onClick={onDismiss} className="absolute top-3 right-3 text-white/60 hover:text-white text-sm">✕</button>
      <div className="flex items-center gap-4">
        <span className="text-4xl">{icon}</span>
        <div className="flex-1">
          <h3 className="text-lg font-bold">{title}</h3>
          <p className="mt-0.5 text-sm opacity-90">{subtitle}</p>
        </div>
        <a href={ctaHref} className="shrink-0 rounded-lg bg-white/20 px-4 py-2 text-sm font-medium backdrop-blur hover:bg-white/30">{ctaLabel}</a>
      </div>
    </div>
  );
}
