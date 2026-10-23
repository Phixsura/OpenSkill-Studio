"use client";

interface RelativeTimeLabelProps { text: string; fullDate: string; showTooltip?: boolean; }

export function RelativeTimeLabel({ text, fullDate, showTooltip = true }: RelativeTimeLabelProps) {
  return (
    <span className="text-xs text-gray-400" title={showTooltip ? fullDate : undefined}>
      {text}
    </span>
  );
}
