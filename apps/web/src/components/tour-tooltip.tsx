"use client";

interface TourStep { id: string; title: string; body: string; position: string; }
interface TourTooltipProps { step: TourStep; currentIndex: number; totalSteps: number;
  onNext: () => void; onSkip: () => void; }

export function TourTooltip({ step, currentIndex, totalSteps, onNext, onSkip }: TourTooltipProps) {
  const isLast = currentIndex === totalSteps - 1;
  return (
    <div className="rounded-xl border bg-white dark:bg-gray-900 dark:border-gray-700 shadow-xl p-4 max-w-xs">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">{currentIndex + 1}/{totalSteps}</span>
        <button onClick={onSkip} className="text-xs text-gray-400 hover:text-gray-600">Skip</button>
      </div>
      <h4 className="text-sm font-bold mb-1">{step.title}</h4>
      <p className="text-xs text-gray-500 mb-3">{step.body}</p>
      <div className="flex justify-between items-center">
        <div className="flex gap-1">
          {Array.from({ length: totalSteps }, (_, i) => (
            <div key={i} className={`w-1.5 h-1.5 rounded-full ${i <= currentIndex ? "bg-blue-500" : "bg-gray-200"}`} />
          ))}
        </div>
        <button onClick={onNext}
          className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">
          {isLast ? "Finish" : "Next"}
        </button>
      </div>
    </div>
  );
}
