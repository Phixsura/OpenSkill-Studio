"use client";

interface CertificationCardProps { id: string; title: string; icon: string;
  modules: number; passingScore: number; userScore: number | null;
  completed: boolean; onStart: () => void; }

export function CertificationCard({ id, title, icon, modules, passingScore,
  userScore, completed, onStart }: CertificationCardProps) {
  return (
    <div className={`rounded-xl border p-4 ${completed ? "border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-900/10" : "dark:border-gray-700"}`}>
      <div className="text-center mb-2">
        <span className="text-3xl">{icon}</span>
        <h4 className="text-sm font-bold mt-1">{title}</h4>
      </div>
      <div className="text-xs text-gray-400 text-center mb-3">
        <p>{modules} modules · {passingScore}% to pass</p>
        {userScore !== null && (
          <p className={`font-medium ${userScore >= passingScore ? "text-green-600" : "text-red-500"}`}>
            Your score: {userScore}%
          </p>
        )}
      </div>
      {completed ? (
        <div className="text-center text-xs text-green-600 font-medium">✅ Certified</div>
      ) : (
        <button onClick={onStart}
          className="w-full py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
          {userScore !== null ? "Retry" : "Start"}
        </button>
      )}
    </div>
  );
}
