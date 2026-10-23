"use client";

import { useState } from "react";

interface Testimonial { quote: string; author: string; role: string; company: string;
  rating: number; avatar_initials: string; }
interface TestimonialCarouselProps { testimonials: Testimonial[]; avgRating: number; }

export function TestimonialCarousel({ testimonials, avgRating }: TestimonialCarouselProps) {
  const [current, setCurrent] = useState(0);
  if (testimonials.length === 0) return null;
  const t = testimonials[current];
  return (
    <div className="space-y-4">
      <h2 className="text-center text-xl font-bold">What Developers Say</h2>
      <p className="text-center text-sm text-gray-400">⭐ {avgRating} average rating</p>
      <div className="mx-auto max-w-lg rounded-xl bg-gray-50 p-6 text-center dark:bg-gray-800">
        <p className="text-lg italic text-gray-600 dark:text-gray-300">&ldquo;{t.quote}&rdquo;</p>
        <div className="mt-4 flex items-center justify-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
            {t.avatar_initials}
          </div>
          <div className="text-left">
            <p className="text-sm font-bold">{t.author}</p>
            <p className="text-xs text-gray-400">{t.role}{t.company ? ` at ${t.company}` : ""}</p>
          </div>
        </div>
        <p className="mt-2 text-xs text-yellow-500">{"★".repeat(t.rating)}{"☆".repeat(5 - t.rating)}</p>
      </div>
      {testimonials.length > 1 && (
        <div className="flex justify-center gap-1.5">
          {testimonials.map((_, i) => (
            <button key={i} onClick={() => setCurrent(i)}
              className={`h-2 w-2 rounded-full ${i === current ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`} />
          ))}
        </div>
      )}
    </div>
  );
}
