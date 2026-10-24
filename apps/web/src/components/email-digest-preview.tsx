"use client";

interface Section { title: string; value: string; change: number; }
interface EmailDigestPreviewProps { subject: string; developerName: string; period: string;
  sections: Section[]; highlights: string[]; }

export function EmailDigestPreview({ subject, developerName, period, sections, highlights }: EmailDigestPreviewProps) {
  return (
    <div className="mx-auto max-w-md rounded-lg border bg-white p-6 shadow dark:border-gray-700 dark:bg-gray-900">
      <div className="text-center">
        <p className="text-xs text-gray-400">Weekly Digest</p>
        <h2 className="mt-1 text-lg font-bold">Hi {developerName} 👋</h2>
        <p className="text-sm text-gray-400">Here&apos;s your summary for {period}</p>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        {sections.map(s => (
          <div key={s.title} className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
            <p className="text-xs text-gray-400">{s.title}</p>
            <p className="text-lg font-bold">{s.value}</p>
            {s.change !== 0 && (
              <p className={`text-xs ${s.change > 0 ? "text-green-500" : "text-red-500"}`}>
                {s.change > 0 ? "↑" : "↓"} {Math.abs(s.change)}%
              </p>
            )}
          </div>
        ))}
      </div>
      {highlights.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium">🎉 Highlights</h3>
          <ul className="mt-1 space-y-1">
            {highlights.map((h, i) => <li key={i} className="text-sm text-gray-500">• {h}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
