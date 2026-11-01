"use client";

interface Stat { label: string; value: number; icon: string; }
interface Value { title: string; description: string; icon: string; }
interface AboutPageLayoutProps { title: string; subtitle: string; mission: string;
  stats: Stat[]; values: Value[]; }

export function AboutPageLayout({ title, subtitle, mission, stats, values }: AboutPageLayoutProps) {
  return (
    <div className="mx-auto max-w-4xl space-y-12">
      <div className="text-center">
        <h1 className="text-3xl font-bold">{title}</h1>
        <p className="mt-2 text-lg text-gray-500">{subtitle}</p>
      </div>
      <div className="grid grid-cols-4 gap-6 text-center">
        {stats.map(s => (
          <div key={s.label}>
            <span className="text-2xl">{s.icon}</span>
            <p className="mt-1 text-3xl font-bold">{s.value.toLocaleString()}</p>
            <p className="text-sm text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="rounded-xl bg-blue-50 p-8 text-center dark:bg-blue-900/10">
        <h2 className="text-xl font-bold">Our Mission</h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">{mission}</p>
      </div>
      <div>
        <h2 className="text-center text-xl font-bold">Our Values</h2>
        <div className="mt-6 grid grid-cols-2 gap-6">
          {values.map(v => (
            <div key={v.title} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
              <span className="text-2xl">{v.icon}</span>
              <h3 className="mt-2 font-semibold">{v.title}</h3>
              <p className="mt-1 text-sm text-gray-500">{v.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
