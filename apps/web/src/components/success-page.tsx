"use client";

interface SuccessPageProps { title: string; body: string; next: string[];
  showConfetti: boolean; onNext: (step: string) => void; onDone: () => void; }

export function SuccessPage({ title, body, next, showConfetti, onNext, onDone }: SuccessPageProps) {
  return (
    <div className="max-w-md mx-auto text-center py-12">
      {showConfetti && <p className="text-6xl mb-4">🎉</p>}
      <h1 className="text-2xl font-bold mb-2">{title}</h1>
      <p className="text-sm text-gray-500 mb-6">{body}</p>
      {next.length > 0 && (
        <div className="text-left mb-6 space-y-2">
          <p className="text-xs font-semibold text-gray-400">What's next?</p>
          {next.map(s => (
            <button key={s} onClick={() => onNext(s)}
              className="w-full text-left text-sm bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700">
              → {s}
            </button>
          ))}
        </div>
      )}
      <button onClick={onDone}
        className="px-8 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">Done</button>
    </div>
  );
}
