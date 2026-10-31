"use client";

import { useState, useEffect } from "react";

interface Banner { index: number; title: string; subtitle: string; cta_label: string;
  cta_url: string; bg_gradient: string; }
interface BannerCarouselProps { banners: Banner[]; autoRotate: boolean;
  rotateIntervalMs: number; onCtaClick: (url: string) => void; }

export function BannerCarousel({ banners, autoRotate, rotateIntervalMs, onCtaClick }: BannerCarouselProps) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (!autoRotate || banners.length <= 1) return;
    const timer = setInterval(() => setCurrent(c => (c + 1) % banners.length), rotateIntervalMs);
    return () => clearInterval(timer);
  }, [autoRotate, banners.length, rotateIntervalMs]);

  if (banners.length === 0) return null;
  const banner = banners[current];

  return (
    <div className={`rounded-xl bg-gradient-to-r ${banner.bg_gradient} p-8 text-white`}>
      <h2 className="text-2xl font-black">{banner.title}</h2>
      <p className="mt-1 text-sm opacity-80">{banner.subtitle}</p>
      <button onClick={() => onCtaClick(banner.cta_url)}
        className="mt-4 rounded-full bg-white px-6 py-2 text-sm font-bold text-blue-700">
        {banner.cta_label}
      </button>
      {banners.length > 1 && (
        <div className="mt-4 flex justify-center gap-1.5">
          {banners.map((_, i) => (
            <button key={i} onClick={() => setCurrent(i)}
              className={`h-2 w-2 rounded-full ${i === current ? "bg-white" : "bg-white/40"}`} />
          ))}
        </div>
      )}
    </div>
  );
}
