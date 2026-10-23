"use client";

interface Action { label: string; url: string; primary?: boolean; }
interface NotFoundPageProps { title: string; message: string; icon: string; suggestions: string[]; actions: Action[]; }

export function NotFoundPage({ title, message, icon, suggestions, actions }: NotFoundPageProps) {
  return (
    <div className="mx-auto max-w-md py-16 text-center">
      <span className="text-6xl">{icon}</span>
      <h1 className="mt-4 text-2xl font-bold">{title}</h1>
      <p className="mt-2 text-sm text-gray-500">{message}</p>
      <ul className="mt-4 space-y-1">
        {suggestions.map((s, i) => (
          <li key={i} className="text-sm text-gray-400">💡 {s}</li>
        ))}
      </ul>
      <div className="mt-6 flex justify-center gap-3">
        {actions.map(a => (
          <a key={a.label} href={a.url}
            className={`rounded-lg px-4 py-2 text-sm ${a.primary ? "bg-blue-600 text-white" : "border border-gray-200 dark:border-gray-700"}`}>
            {a.label}
          </a>
        ))}
      </div>
    </div>
  );
}
