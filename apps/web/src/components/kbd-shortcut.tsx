"use client";

interface KbdShortcutProps { formattedKeys: string[]; display: string; label?: string; }

export function KbdShortcut({ formattedKeys, display, label }: KbdShortcutProps) {
  return (
    <span className="inline-flex items-center gap-1">
      {label && <span className="text-xs text-gray-400">{label}</span>}
      <kbd className="inline-flex items-center gap-0.5 rounded border bg-gray-50 px-1.5 py-0.5 font-mono text-xs text-gray-500 dark:border-gray-600 dark:bg-gray-800">
        {formattedKeys.map((k, i) => (
          <span key={i}>{k}</span>
        ))}
      </kbd>
    </span>
  );
}
