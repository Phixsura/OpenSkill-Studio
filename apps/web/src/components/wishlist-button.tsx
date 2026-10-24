"use client";

interface WishlistButtonProps { wishlisted: boolean; count: number; onToggle: () => void; }

export function WishlistButton({ wishlisted, count, onToggle }: WishlistButtonProps) {
  return (
    <button onClick={onToggle}
      className={`inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg transition ${
        wishlisted ? "bg-red-50 text-red-600 dark:bg-red-900/20" : "bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-red-500"
      }`}>
      <span>{wishlisted ? "❤️" : "🤍"}</span>
      <span>{wishlisted ? "Wishlisted" : "Add to Wishlist"}</span>
      {count > 0 && <span className="text-xs text-gray-400">({count})</span>}
    </button>
  );
}
