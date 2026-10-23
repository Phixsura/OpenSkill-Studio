"use client";

import { useState } from "react";

interface StarRatingInputProps { maxStars: number; value: number; labels: Record<number, string>;
  onChange: (value: number) => void; readOnly?: boolean; }

export function StarRatingInput({ maxStars, value, labels, onChange, readOnly }: StarRatingInputProps) {
  const [hovered, setHovered] = useState<number | null>(null);
  const displayValue = hovered ?? value;

  return (
    <div className="space-y-1">
      <div className="flex gap-0.5">
        {Array.from({ length: maxStars }, (_, i) => i + 1).map(star => (
          <button key={star} disabled={readOnly}
            onMouseEnter={() => !readOnly && setHovered(star)}
            onMouseLeave={() => setHovered(null)}
            onClick={() => !readOnly && onChange(star)}
            className={`text-2xl transition-colors ${star <= displayValue ? "text-yellow-400" : "text-gray-300 dark:text-gray-600"} ${readOnly ? "cursor-default" : "cursor-pointer hover:scale-110"}`}>
            ★
          </button>
        ))}
      </div>
      {labels[displayValue] && (
        <p className="text-xs text-gray-500">{labels[displayValue]}</p>
      )}
    </div>
  );
}
