"use client";

interface UiBadgeProps { label: string; variant?: string; icon?: string; dot?: boolean; size?: string; }

const VARIANT_CLASS: Record<string, string> = {
  default: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  primary: "bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400",
  success: "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400",
  warning: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400",
  danger: "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400",
  info: "bg-purple-100 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400",
};
const DOT_COLOR: Record<string, string> = {
  success: "bg-green-500", warning: "bg-yellow-500", danger: "bg-red-500",
  primary: "bg-blue-500", info: "bg-purple-500", default: "bg-gray-400",
};

export function UiBadge({ label, variant = "default", icon, dot, size = "sm" }: UiBadgeProps) {
  const sizeClass = size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-3 py-1";
  return (
    <span className={`inline-flex items-center gap-1 rounded-full font-medium ${sizeClass} ${VARIANT_CLASS[variant] || VARIANT_CLASS.default}`}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${DOT_COLOR[variant] || DOT_COLOR.default}`} />}
      {icon && <span>{icon}</span>}
      {label}
    </span>
  );
}
