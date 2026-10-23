"use client";

interface ResponsiveGridProps { children: React.ReactNode; columns?: { mobile?: number; tablet?: number; desktop?: number }; gap?: number; }

export function ResponsiveGrid({ children, columns = { mobile: 1, tablet: 2, desktop: 4 }, gap = 4 }: ResponsiveGridProps) {
  const colClasses: Record<number, string> = {
    1: "grid-cols-1", 2: "grid-cols-2", 3: "grid-cols-3", 4: "grid-cols-4",
  };
  const gapClasses: Record<number, string> = { 2: "gap-2", 3: "gap-3", 4: "gap-4", 6: "gap-6", 8: "gap-8" };

  return (
    <div className={`grid ${colClasses[columns.mobile || 1]} sm:${colClasses[columns.tablet || 2]} lg:${colClasses[columns.desktop || 4]} ${gapClasses[gap] || "gap-4"}`}>
      {children}
    </div>
  );
}
