"use client";

interface ResponsiveCardGridProps { gridClass: string; children: React.ReactNode;
  itemsCount: number; emptyMessage?: string; }

export function ResponsiveCardGrid({ gridClass, children, itemsCount, emptyMessage }: ResponsiveCardGridProps) {
  if (itemsCount === 0) {
    return (
      <div className="flex min-h-[200px] items-center justify-center">
        <p className="text-sm text-gray-400">{emptyMessage ?? "No items to display"}</p>
      </div>
    );
  }
  return <div className={gridClass}>{children}</div>;
}
