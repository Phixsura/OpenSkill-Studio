"use client";

interface LinkPreviewCardProps { url: string; title: string; description: string;
  imageUrl: string | null; domain: string; hasImage: boolean; onClick: () => void; }

export function LinkPreviewCard({ url, title, description, imageUrl, domain, hasImage, onClick }: LinkPreviewCardProps) {
  return (
    <button onClick={onClick}
      className="flex w-full overflow-hidden rounded-lg border text-left hover:shadow dark:border-gray-700">
      {hasImage && imageUrl && (
        <div className="w-32 flex-shrink-0 bg-gray-100 dark:bg-gray-800">
          <div className="flex h-full items-center justify-center text-3xl text-gray-300">🖼️</div>
        </div>
      )}
      <div className="flex-1 p-3">
        <p className="text-[10px] text-gray-400">{domain}</p>
        <h3 className="mt-0.5 text-sm font-semibold line-clamp-1">{title}</h3>
        <p className="mt-0.5 text-xs text-gray-500 line-clamp-2">{description}</p>
      </div>
    </button>
  );
}
