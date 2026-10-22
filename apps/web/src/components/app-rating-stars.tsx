"use client";

interface AppRatingStarsProps {
  rating: number;
  count: number;
  size?: "sm" | "md";
}

export function AppRatingStars({ rating, count, size = "sm" }: AppRatingStarsProps) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating - fullStars >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);
  const sizeClass = size === "md" ? "text-lg" : "text-sm";

  return (
    <span className={`inline-flex items-center gap-1 ${sizeClass}`}>
      {"★".repeat(fullStars)}
      {hasHalf && "½"}
      {"☆".repeat(emptyStars)}
      <span className="text-xs text-gray-500">({count})</span>
    </span>
  );
}
