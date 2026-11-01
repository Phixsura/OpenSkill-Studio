"use client";
export function FleetIdpPanel({ templates, scaffolds, docsPages, adoptionScore }: { templates: number; scaffolds: number; docsPages: number; adoptionScore: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ Developer Portal</h3>
    <div className="text-sm">{templates} templates · {scaffolds} scaffolds/30d · {docsPages} docs</div>
    <div className="text-xs text-blue-500">Adoption: {adoptionScore}</div>
  </div>);
}
