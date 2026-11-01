"use client";

interface EmailSection { type: string; emoji: string; items: string[]; count: number; }
interface ChangelogEmailPreviewProps { subject: string; greeting: string;
  version: string; sections: EmailSection[]; totalChanges: number; }

export function ChangelogEmailPreview({ subject, greeting, version, sections, totalChanges }: ChangelogEmailPreviewProps) {
  return (
    <div className="max-w-lg mx-auto rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="bg-blue-600 text-white px-5 py-3">
        <p className="text-xs opacity-75">Email Preview</p>
        <h3 className="font-bold">{subject}</h3>
      </div>
      <div className="p-5 bg-white dark:bg-gray-900 space-y-4">
        <p className="text-sm">{greeting}</p>
        <p className="text-sm text-gray-500">Here&apos;s what&apos;s new in <strong>v{version}</strong>:</p>
        {sections.map(s => (
          <div key={s.type}>
            <h4 className="text-sm font-semibold mb-1">{s.emoji} {s.type.charAt(0).toUpperCase() + s.type.slice(1)} ({s.count})</h4>
            <ul className="text-sm text-gray-600 space-y-0.5 ml-4">
              {s.items.map((item, i) => <li key={i}>• {item}</li>)}
            </ul>
          </div>
        ))}
        <p className="text-xs text-gray-400">{totalChanges} total changes</p>
      </div>
    </div>
  );
}
