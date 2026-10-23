"use client";

interface CardPreview { name: string; icon: string; tagline: string; rating: number;
  installsDisplay: string; priceDisplay: string; verified: boolean; category: string; }
interface Completeness { pct: number; ready: boolean; filled: number; total: number; }
interface ListingPreviewCardProps { preview: CardPreview; completeness: Completeness; }

export function ListingPreviewCard({ preview, completeness }: ListingPreviewCardProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <p className="text-xs text-gray-400 mb-2">Card Preview</p>
        <div className="flex items-start gap-3">
          <span className="text-3xl">{preview.icon}</span>
          <div className="flex-1">
            <div className="flex items-center gap-1.5">
              <h4 className="font-bold">{preview.name}</h4>
              {preview.verified && <span className="text-blue-500 text-xs">✓</span>}
            </div>
            <p className="text-xs text-gray-500">{preview.tagline}</p>
            <div className="flex gap-2 mt-1 text-xs text-gray-400">
              <span>⭐ {preview.rating}</span>
              <span>📥 {preview.installsDisplay}</span>
              <span>{preview.priceDisplay}</span>
              <span className="capitalize">{preview.category}</span>
            </div>
          </div>
        </div>
      </div>
      <div className="rounded-lg border dark:border-gray-700 p-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium">Completeness</span>
          <span className={`text-xs ${completeness.ready ? "text-green-600" : "text-yellow-600"}`}>
            {completeness.pct}% · {completeness.filled}/{completeness.total}
          </span>
        </div>
        <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${completeness.ready ? "bg-green-500" : "bg-yellow-500"}`}
               style={{ width: `${completeness.pct}%` }} />
        </div>
      </div>
    </div>
  );
}
