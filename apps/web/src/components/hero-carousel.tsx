"use client";

import { useState, useEffect } from "react";

interface Slide { name: string; tagline: string; category: string; ctaUrl: string; }
interface HeroCarouselProps { slides: Slide[]; intervalMs?: number; }

const ICONS: Record<string, string> = { connector: "🔌", automation: "🤖", analytics: "📊", ui_extension: "🖥️" };

export function HeroCarousel({ slides, intervalMs = 5000 }: HeroCarouselProps) {
  const [current, setCurrent] = useState(0);
  useEffect(() => {
    if (slides.length <= 1) return;
    const timer = setInterval(() => setCurrent(c => (c + 1) % slides.length), intervalMs);
    return () => clearInterval(timer);
  }, [slides.length, intervalMs]);

  if (slides.length === 0) return null;
  const slide = slides[current];
  return (
    <div className="rounded-xl bg-gradient-to-r from-indigo-600 to-blue-500 p-6 text-white">
      <span className="text-3xl">{ICONS[slide.category] ?? "📦"}</span>
      <h3 className="mt-2 text-xl font-bold">{slide.name}</h3>
      <p className="mt-1 opacity-80">{slide.tagline}</p>
      <a href={slide.ctaUrl} className="mt-3 inline-block rounded bg-white px-4 py-1.5 text-sm font-medium text-blue-600">Learn More</a>
      {slides.length > 1 && (
        <div className="mt-3 flex gap-1">{slides.map((_, i) => (
          <span key={i} className={`h-1.5 w-6 rounded-full ${i === current ? "bg-white" : "bg-white/30"}`} />
        ))}</div>
      )}
    </div>
  );
}
