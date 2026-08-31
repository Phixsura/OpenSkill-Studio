"use client";

import dynamic from "next/dynamic";
import { useParams } from "next/navigation";

// React Flow is client-only — load the editor without SSR
const WorkflowEditor = dynamic(() => import("@/components/workflow-editor/editor"), {
  ssr: false,
  loading: () => (
    <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading editor…</p>
  ),
});

export default function WorkflowEditorPage() {
  const { orgId, packId } = useParams<{ orgId: string; packId: string }>();
  return <WorkflowEditor orgId={orgId} packId={packId} />;
}
