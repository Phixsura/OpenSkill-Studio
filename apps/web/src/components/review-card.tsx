"use client";

interface ReviewCardProps { author: string; avatarInitials: string; rating: number;
  stars: string; title: string; body: string; helpfulCount: number; dateDisplay: string;
  hasResponse: boolean; developerResponse: string | null;
  onHelpful: () => void; }

export function ReviewCard({ author, avatarInitials, rating, stars, title, body,
  helpfulCount, dateDisplay, hasResponse, developerResponse, onHelpful }: ReviewCardProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-bold dark:bg-gray-700">
          {avatarInitials}
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">{author}</span>
              <span className="ml-2 text-xs text-yellow-500">{stars}</span>
            </div>
            <span className="text-xs text-gray-400">{dateDisplay}</span>
          </div>
          <h4 className="mt-1 text-sm font-semibold">{title}</h4>
          <p className="mt-1 text-sm text-gray-500">{body}</p>
          <button onClick={onHelpful}
            className="mt-2 rounded border px-2 py-0.5 text-xs text-gray-400 hover:text-blue-500 dark:border-gray-600">
            👍 Helpful ({helpfulCount})
          </button>
        </div>
      </div>
      {hasResponse && developerResponse && (
        <div className="ml-12 mt-3 rounded bg-blue-50 p-3 dark:bg-blue-900/10">
          <p className="text-xs font-medium text-blue-700 dark:text-blue-400">Developer Response</p>
          <p className="mt-0.5 text-sm text-gray-600 dark:text-gray-300">{developerResponse}</p>
        </div>
      )}
    </div>
  );
}
