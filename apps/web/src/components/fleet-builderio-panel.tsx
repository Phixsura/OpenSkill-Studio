"use client";
export function FleetBuilderioPanel({ spaces, active, pages, components }: { spaces: number; active: number; pages: number; components: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Builder.io</h3>
    <div className="text-sm">{active}/{spaces} active · {pages} pages · {components} components</div>
  </div>);
}
