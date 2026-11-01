"use client";

interface SectionInfo { section_id: string; title: string; has_code: boolean; language: string; }
interface Props { sections: SectionInfo[]; appName: string; }

export default function APIDeveloperGettingStartedCard({ sections, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Getting Started</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{sections.length} sections</span>
      </div>
      {sections.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No getting started content</p>
      ) : (
        <div className="space-y-0.5">
          {sections.map((s, i) => (
            <div key={s.section_id} className="flex items-center gap-2 text-[11px]">
              <span className="text-gray-400">{i + 1}.</span>
              <span className="text-gray-700 dark:text-gray-300">{s.title}</span>
              {s.has_code && <span className="rounded bg-gray-100 px-1 py-0.5 text-[8px] text-gray-500 dark:bg-gray-800">{s.language}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
