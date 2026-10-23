"use client";

interface FormattedNumberProps { value: number; style?: "compact" | "currency" | "percentage" | "decimal";
  prefix?: string; suffix?: string; className?: string; }

function formatCompact(val: number): string {
  if (Math.abs(val) >= 1e9) return `${(val / 1e9).toFixed(1)}B`;
  if (Math.abs(val) >= 1e6) return `${(val / 1e6).toFixed(1)}M`;
  if (Math.abs(val) >= 1e3) return `${(val / 1e3).toFixed(1)}K`;
  return val % 1 === 0 ? String(val) : val.toFixed(1);
}

export function FormattedNumber({ value, style = "compact", prefix, suffix, className }: FormattedNumberProps) {
  let display: string;
  switch (style) {
    case "currency": display = `$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`; break;
    case "percentage": display = `${value.toFixed(1)}%`; break;
    case "decimal": display = value.toLocaleString(undefined, { minimumFractionDigits: 2 }); break;
    default: display = formatCompact(value);
  }
  return <span className={className}>{prefix}{display}{suffix}</span>;
}
