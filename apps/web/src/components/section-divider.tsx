"use client";

interface SectionDividerProps { label: string | null; variantClass: string; spacingClass: string; }

export function SectionDivider({ label, variantClass, spacingClass }: SectionDividerProps) {
  if (!label) {
    return <div className={`${variantClass} ${spacingClass} dark:border-gray-700`} />;
  }
  return (
    <div className={`${spacingClass} flex items-center gap-3`}>
      <div className={`flex-1 ${variantClass} dark:border-gray-700`} />
      <span className="text-xs text-gray-400">{label}</span>
      <div className={`flex-1 ${variantClass} dark:border-gray-700`} />
    </div>
  );
}
