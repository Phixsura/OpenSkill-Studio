"use client";

interface Section { title: string; icon: string; items: string[]; }
interface ChangelogEmailPreviewProps { subject: string; sections: Section[]; totalChanges: number; recipientCount: number; onSend: () => void; }

export function ChangelogEmailPreview({ subject, sections, totalChanges, recipientCount, onSend }: ChangelogEmailPreviewProps) {
  return (
    <div className="mx-auto max-w-lg rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="border-b p-4 dark:border-gray-700">
        <p className="text-xs text-gray-400">Email Preview</p>
        <h3 className="mt-1 font-semibold">{subject}</h3>
        <p className="text-xs text-gray-400">{recipientCount.toLocaleString()} recipients · {totalChanges} changes</p>
      </div>
      <div className="space-y-3 p-4">
        {sections.map((s, i) => (
          <div key={i}>
            <h4 className="text-sm font-semibold">{s.icon} {s.title}</h4>
            <ul className="mt-1 list-inside list-disc text-sm text-gray-600 dark:text-gray-400">
              {s.items.map((item, j) => <li key={j}>{item}</li>)}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t p-4 dark:border-gray-700">
        <button onClick={onSend} className="w-full rounded bg-blue-600 py-2 text-sm text-white">
          Send to {recipientCount.toLocaleString()} users
        </button>
      </div>
    </div>
  );
}
