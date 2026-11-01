"use client";

interface Component { name: string; version: string; status: string; }
interface AboutPageProps { appName: string; version: string; runtime: string;
  components: Component[]; links: Record<string, string>; }

export function AboutPage({ appName, version, runtime, components, links }: AboutPageProps) {
  return (
    <div className="space-y-5 max-w-lg mx-auto">
      <div className="text-center">
        <h1 className="text-2xl font-bold">{appName}</h1>
        <p className="text-sm text-gray-400">v{version} · {runtime}</p>
      </div>
      <div className="space-y-2">
        <h3 className="text-sm font-semibold">Components</h3>
        {components.map(c => (
          <div key={c.name} className="flex items-center justify-between rounded-lg border px-4 py-2 dark:border-gray-700">
            <span className="text-sm">{c.name}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{c.version}</span>
              <span className="h-2 w-2 rounded-full bg-green-500" />
            </div>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-4 text-xs">
        {Object.entries(links).map(([label, href]) => (
          <a key={label} href={href} className="text-blue-600 hover:underline capitalize">{label.replace("_", " ")}</a>
        ))}
      </div>
    </div>
  );
}
