"use client";

interface ChangelogEmailPreviewProps { subject: string; bodyHtml: string;
  recipientCount: number; changeCount: number; hasBreaking: boolean;
  onSend: () => void; onEdit: () => void; }

export function ChangelogEmailPreview({ subject, bodyHtml, recipientCount, changeCount,
  hasBreaking, onSend, onEdit }: ChangelogEmailPreviewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Email Preview</h2>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span>{changeCount} changes</span>
          <span>{recipientCount} recipients</span>
          {hasBreaking && <span className="text-red-500">⚠️ Breaking</span>}
        </div>
      </div>
      <div className="rounded-lg border dark:border-gray-700">
        <div className="border-b bg-gray-50 px-4 py-2 dark:border-gray-700 dark:bg-gray-800">
          <p className="text-xs text-gray-400">Subject:</p>
          <p className="text-sm font-medium">{subject}</p>
        </div>
        <div className="prose prose-sm max-w-none p-4 dark:prose-invert"
          dangerouslySetInnerHTML={{ __html: bodyHtml }} />
      </div>
      <div className="flex gap-2">
        <button onClick={onEdit} className="flex-1 rounded border py-2 text-sm dark:border-gray-600">Edit</button>
        <button onClick={onSend} className="flex-1 rounded bg-green-600 py-2 text-sm text-white">
          Send to {recipientCount} subscribers
        </button>
      </div>
    </div>
  );
}
