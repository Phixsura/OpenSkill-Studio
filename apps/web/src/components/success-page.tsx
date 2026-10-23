"use client";

interface NextStep { label: string; url: string; primary: boolean; }
interface SuccessPageProps { title: string; icon: string; message: string;
  nextSteps: NextStep[]; onNavigate: (url: string) => void; }

export function SuccessPage({ title, icon, message, nextSteps, onNavigate }: SuccessPageProps) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="mx-auto max-w-md space-y-6 text-center">
        <span className="text-6xl">{icon}</span>
        <h1 className="text-2xl font-black">{title}</h1>
        <p className="text-sm text-gray-500">{message}</p>
        <div className="flex justify-center gap-3">
          {nextSteps.map(step => (
            <button key={step.label} onClick={() => onNavigate(step.url)}
              className={`rounded-lg px-5 py-2.5 text-sm font-semibold ${step.primary ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
              {step.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
