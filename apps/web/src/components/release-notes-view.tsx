"use client";

interface Section { type: string; content: string; }
interface ReleaseNotesViewProps { version: string; sections: Section[]; breaking: boolean; }

const TYPE_ICONS: Record<string, string> = { breaking: "⚠️", permissions: "🔑", notes: "📝", diff: "📊" };

export function ReleaseNotesView({ version, sections, breaking }: ReleaseNotesViewProps) {
  return (
    <div className={`rounded-lg border p-4 ${breaking ? "border-red-200 dark:border-red-800" : "border-gray-200 dark:border-gray-700"}`}>
      <h4 className="mb-2 font-semibold">v{version} {breaking && <span className="text-red-600">⚠️ Breaking</span>}</h4>
      <div className="space-y-2">
        {sections.map((s, i) => (
          <div key={i} className="text-sm">
            <span>{TYPE_ICONS[s.type] ?? "•"}</span> {s.content}
          </div>
        ))}
      </div>
    </div>
  );
}
