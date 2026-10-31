"use client";
export function FleetApiDocumentationV9Panel({ apis, documented }: { apis: number; documented: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 API Docs v9</h3>
    <div className="text-sm">{apis} APIs · {documented} documented</div>
  </div>);
}
