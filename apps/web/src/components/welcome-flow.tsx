"use client";

interface WelcomeStep { stepId: string; title: string; content: string; actionLabel: string; completed: boolean; }
interface Progress { completed: number; total: number; percentage: number; allDone: boolean; }

export function WelcomeFlow({ steps, progress, onComplete, onSkip }: {
  steps: WelcomeStep[]; progress: Progress;
  onComplete?: (stepId: string) => void; onSkip?: () => void;
}) {
  if (progress.allDone) return null;
  return (
    <div className="border dark:border-gray-700 rounded-xl overflow-hidden">
      <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-4 text-white">
        <div className="flex justify-between items-center">
          <div>
            <span className="font-bold block">Welcome to OpenSkill Marketplace! 🎉</span>
            <span className="text-sm opacity-80">{progress.completed}/{progress.total} steps completed</span>
          </div>
          <button onClick={onSkip} className="text-xs opacity-60 hover:opacity-100">Skip all</button>
        </div>
        <div className="h-1.5 bg-white/20 rounded-full mt-2">
          <div className="h-full bg-white rounded-full transition-all" style={{ width: `${progress.percentage}%` }} />
        </div>
      </div>
      <div className="p-4 space-y-2">
        {steps.filter(s => !s.completed).slice(0, 3).map(s => (
          <div key={s.stepId} className="flex items-center justify-between border dark:border-gray-700 rounded-lg p-3">
            <div>
              <span className="font-medium text-sm">{s.title}</span>
              <p className="text-xs text-gray-500">{s.content}</p>
            </div>
            <button onClick={() => onComplete?.(s.stepId)}
              className="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-lg shrink-0">{s.actionLabel}</button>
          </div>
        ))}
      </div>
    </div>
  );
}
