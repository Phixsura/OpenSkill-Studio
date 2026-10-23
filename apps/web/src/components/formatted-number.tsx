"use client";

interface FormattedNumberProps { value: number; format: "compact" | "currency" | "percentage" | "bytes";
  currency?: string; className?: string; }

function fmtCompact(n: number): string {
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
  return n.toString();
}

export function FormattedNumber({ value, format, currency = "USD", className = "" }: FormattedNumberProps) {
  let display: string;
  if (format === "compact") display = fmtCompact(value);
  else if (format === "currency") display = `$${value.toLocaleString()}`;
  else if (format === "percentage") display = `${value.toFixed(1)}%`;
  else display = `${value} B`;
  return <span className={`font-mono ${className}`}>{display}</span>;
}
