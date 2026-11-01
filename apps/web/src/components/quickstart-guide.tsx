"use client";

interface Section { title: string; content: string; }
interface QuickstartGuideProps { appName: string; sections: Section[]; setupMinutes: number; }

export function QuickstartGuide({ appName, sections, setupMinutes }: QuickstartGuideProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-6 dark:border-gray-700">
      <h2 className="text-xl font-bold">Getting Started with {appName}</h2>
      <p className="mt-1 text-sm text-gray-500">⏱️ Estimated setup: {setupMinutes} minutes</p>
      <div className="mt-4 space-y-6">
        {sections.map((s, i) => (
          <div key={i}>
            <h3 className="text-lg font-semibold">{s.title}</h3>
            <div className="mt-1 whitespace-pre-line text-sm text-gray-600 dark:text-gray-400">{s.content}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
