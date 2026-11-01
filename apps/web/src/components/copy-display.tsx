"use client";

interface CopyDisplayProps { text: string; variant?: "label" | "description" | "error" | "success"; }

const VARIANT_CLASSES: Record<string, string> = {
  label: "text-sm font-medium text-gray-700 dark:text-gray-300",
  description: "text-sm text-gray-500 dark:text-gray-400",
  error: "text-sm text-red-600 dark:text-red-400",
  success: "text-sm text-green-600 dark:text-green-400",
};

export function CopyDisplay({ text, variant = "description" }: CopyDisplayProps) {
  return <p className={VARIANT_CLASSES[variant] || VARIANT_CLASSES.description}>{text}</p>;
}
