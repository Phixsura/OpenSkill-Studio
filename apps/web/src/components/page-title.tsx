"use client";

interface PageTitleProps { title: string; subtitle?: string; actions?: React.ReactNode; }

export function PageTitle({ title, subtitle, actions }: PageTitleProps) {
  return (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-bold">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
      </div>
      {actions && <div>{actions}</div>}
    </div>
  );
}
