"use client";

interface Certification { id: string; label: string; icon: string; required_score: number; completed: boolean; }
interface CertificationProgressCardProps { certifications: Certification[];
  completed: number; total: number; progressPct: number; onTakeExam: (id: string) => void; }

export function CertificationProgressCard({ certifications, completed, total, progressPct, onTakeExam }: CertificationProgressCardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Certifications</h2>
        <span className="text-sm font-bold">{completed}/{total}</span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-purple-500" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {certifications.map(c => (
          <div key={c.id} className={`rounded-lg border p-3 ${c.completed ? "border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-900/10" : "dark:border-gray-700"}`}>
            <div className="flex items-center gap-2">
              <span className="text-2xl">{c.icon}</span>
              <div>
                <p className="font-medium">{c.label}</p>
                <p className="text-xs text-gray-400">Required: {c.required_score}%</p>
              </div>
            </div>
            {c.completed ? (
              <p className="mt-2 text-center text-xs text-green-600">✅ Certified</p>
            ) : (
              <button onClick={() => onTakeExam(c.id)}
                className="mt-2 w-full rounded bg-purple-600 py-1 text-xs text-white">Take Exam</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
