"use client";

interface ReviewResponseCardProps { rating: number; title: string; body: string; author: string;
  responseBody: string | null; respondedAt: string | null; onRespond: () => void; }

export function ReviewResponseCard({ rating, title, body, author, responseBody, respondedAt, onRespond }: ReviewResponseCardProps) {
  const stars = "★".repeat(rating) + "☆".repeat(5 - rating);
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center gap-2">
        <span className="text-yellow-500 text-xs">{stars}</span>
        <span className="text-sm font-medium">{title}</span>
      </div>
      <p className="mt-1 text-sm text-gray-500">{body}</p>
      <p className="mt-1 text-xs text-gray-400">by {author}</p>
      {responseBody ? (
        <div className="mt-3 rounded-lg bg-blue-50 p-3 dark:bg-blue-900/10">
          <p className="text-xs font-semibold text-blue-700 dark:text-blue-300 mb-1">Developer Response</p>
          <p className="text-sm">{responseBody}</p>
          {respondedAt && <p className="mt-1 text-xs text-gray-400">{respondedAt}</p>}
        </div>
      ) : (
        <button onClick={onRespond} className="mt-2 text-xs text-blue-600 hover:underline">Reply to review</button>
      )}
    </div>
  );
}
