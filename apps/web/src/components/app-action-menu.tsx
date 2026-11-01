"use client";

import { useState } from "react";

interface AppActionMenuProps {
  appStatus: string;
  onEdit?: () => void;
  onSubmitReview?: () => void;
  onPublish?: () => void;
  onDeprecate?: () => void;
  onRevoke?: () => void;
  onDelete?: () => void;
}

export function AppActionMenu({ appStatus, onEdit, onSubmitReview, onPublish, onDeprecate, onRevoke, onDelete }: AppActionMenuProps) {
  const [open, setOpen] = useState(false);

  const actions = [
    onEdit && { label: "✏️ Edit", handler: onEdit, show: true },
    onSubmitReview && { label: "📝 Submit for Review", handler: onSubmitReview, show: ["draft", "testing"].includes(appStatus) },
    onPublish && { label: "🚀 Publish", handler: onPublish, show: appStatus === "approved" },
    onDeprecate && { label: "📦 Deprecate", handler: onDeprecate, show: appStatus === "published" },
    onRevoke && { label: "🚫 Revoke", handler: onRevoke, show: ["published", "deprecated"].includes(appStatus) },
    onDelete && { label: "🗑️ Delete", handler: onDelete, show: appStatus === "draft" },
  ].filter((a): a is { label: string; handler: () => void; show: boolean } => !!a && a.show);

  if (actions.length === 0) return null;

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} className="rounded border px-3 py-1 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
        Actions ▾
      </button>
      {open && (
        <div className="absolute right-0 z-10 mt-1 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-900">
          {actions.map(a => (
            <button key={a.label} onClick={() => { a.handler(); setOpen(false); }}
              className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
              {a.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
