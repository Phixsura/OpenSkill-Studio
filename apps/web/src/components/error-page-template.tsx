"use client";

interface Action { label: string; href: string; primary: boolean; }
interface ErrorPageTemplateProps { code: number; title: string; icon: string;
  message: string; appName: string; requestId: string | null; actions: Action[]; }

export function ErrorPageTemplate({ code, title, icon, message, appName, requestId, actions }: ErrorPageTemplateProps) {
  return (
    <div className="flex min-h-[500px] flex-col items-center justify-center text-center p-8">
      <span className="text-7xl mb-6">{icon}</span>
      <h1 className="text-5xl font-extrabold text-gray-900 dark:text-white">{code}</h1>
      <h2 className="mt-3 text-xl font-semibold">{title}</h2>
      <p className="mt-2 max-w-md text-gray-500">{message}</p>
      <div className="mt-8 flex gap-3">
        {actions.map(a => (
          <a key={a.label} href={a.href}
            className={`rounded-lg px-5 py-2.5 text-sm font-medium ${a.primary ? "bg-blue-600 text-white" : "border dark:border-gray-700"}`}>
            {a.label}
          </a>
        ))}
      </div>
      {requestId && <p className="mt-6 text-xs text-gray-400">Request ID: {requestId}</p>}
      <p className="mt-2 text-xs text-gray-300">{appName}</p>
    </div>
  );
}
