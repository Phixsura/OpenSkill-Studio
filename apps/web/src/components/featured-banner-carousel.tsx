"use client";
import { useState } from "react";

interface Banner { title: string; subtitle: string; cta: string; link: string;
  bgGradient: string; icon: string; }
interface FeaturedBannerCarouselProps { banners: Banner[]; onCta: (link: string) => void; }

export function FeaturedBannerCarousel({ banners, onCta }: FeaturedBannerCarouselProps) {
  const [idx, setIdx] = useState(0);
  if (!banners.length) return null;
  const b = banners[idx];
  return (
    <div className={`rounded-2xl bg-gradient-to-r ${b.bgGradient} p-8 text-white relative`}>
      <div className="max-w-lg">
        <p className="text-3xl mb-2">{b.icon}</p>
        <h2 className="text-2xl font-bold mb-1">{b.title}</h2>
        <p className="text-sm opacity-90 mb-4">{b.subtitle}</p>
        <button onClick={() => onCta(b.link)}
          className="px-5 py-2 bg-white text-gray-900 rounded-lg text-sm font-medium hover:bg-gray-100">{b.cta}</button>
      </div>
      {banners.length > 1 && (
        <div className="absolute bottom-4 right-4 flex gap-1">
          {banners.map((_, i) => (
            <button key={i} onClick={() => setIdx(i)}
              className={`w-2 h-2 rounded-full ${i === idx ? "bg-white" : "bg-white/40"}`} />
          ))}
        </div>
      )}
    </div>
  );
}
