"use client";

export function UplatformUnotificationUbadge({ label = "OpenSkill" }: { label?: string }) {
  return <div className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</div>;
}
