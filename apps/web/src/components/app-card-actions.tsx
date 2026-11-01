"use client";

interface CardAction { id: string; label: string; icon: string; variant: string; }
interface AppCardActionsProps { actions: CardAction[]; onAction: (id: string) => void; }

const VARIANT_STYLE: Record<string, string> = {
  primary: "bg-blue-600 text-white hover:bg-blue-700",
  danger: "bg-red-100 text-red-700 hover:bg-red-200",
  secondary: "bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700",
};

export function AppCardActions({ actions, onAction }: AppCardActionsProps) {
  return (
    <div className="flex gap-1.5 flex-wrap">
      {actions.map(a => (
        <button key={a.id} onClick={() => onAction(a.id)}
          className={`text-xs px-2.5 py-1 rounded-lg font-medium ${VARIANT_STYLE[a.variant] || VARIANT_STYLE.secondary}`}>
          {a.icon} {a.label}
        </button>
      ))}
    </div>
  );
}
