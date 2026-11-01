"use client";

interface CountBadgeProps { count: number; display: string; visible: boolean;
  size: string; urgency: string; }

const sizeClass: Record<string, string> = {
  sm: "h-5 min-w-[1.25rem] text-[10px]",
  md: "h-5 min-w-[1.5rem] text-xs",
  lg: "h-6 min-w-[1.75rem] text-xs",
};
const urgencyColor: Record<string, string> = {
  high: "bg-red-500", medium: "bg-orange-500", low: "bg-blue-500",
};

export function CountBadge({ count, display, visible, size, urgency }: CountBadgeProps) {
  if (!visible) return null;
  return (
    <span className={`inline-flex items-center justify-center rounded-full px-1.5 font-bold text-white ${sizeClass[size] ?? sizeClass.sm} ${urgencyColor[urgency] ?? urgencyColor.low}`}>
      {display}
    </span>
  );
}
