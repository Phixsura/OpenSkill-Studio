"use client";

interface WishlistButtonProps { isWishlisted: boolean; onToggle: () => void; count?: number; }

export function WishlistButton({ isWishlisted, onToggle, count }: WishlistButtonProps) {
  return (
    <button onClick={onToggle}
      className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition ${
        isWishlisted
          ? "border-red-300 bg-red-50 text-red-600 dark:border-red-700 dark:bg-red-900/20"
          : "border-gray-200 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
      }`}>
      <span>{isWishlisted ? "❤️" : "🤍"}</span>
      <span>{isWishlisted ? "Wishlisted" : "Add to Wishlist"}</span>
      {count != null && <span className="text-xs opacity-60">({count})</span>}
    </button>
  );
}
