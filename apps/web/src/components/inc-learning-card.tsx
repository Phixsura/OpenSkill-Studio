"use client";

interface Lesson { area: string; lesson: string; priority: string; }
interface IncLearningCardProps { incidentId: string; lessons: Lesson[];
  lessonCount: number; byArea: Record<string, number>; }

const PRIORITY_COLORS: Record<string, string> = {
  high: "bg-red-100 text-red-700", medium: "bg-yellow-100 text-yellow-700", low: "bg-blue-100 text-blue-700",
};

export function IncLearningCard({ incidentId, lessons, lessonCount, byArea }: IncLearningCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📖 Learnings: {incidentId}</h3>
        <span className="text-xs text-gray-400">{lessonCount} lessons</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {lessons.map((l, i) => (
          <div key={i} className="px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`px-1.5 py-0.5 rounded text-[10px] ${PRIORITY_COLORS[l.priority] ?? ""}`}>{l.priority}</span>
              <span className="text-gray-400">{l.area}</span>
            </div>
            <div className="mt-0.5">{l.lesson}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
