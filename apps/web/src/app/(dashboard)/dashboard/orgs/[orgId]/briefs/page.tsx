"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

interface ClientBrief {
  id: string;
  title: string;
  slug: string;
  client_name: string;
  project_type: string;
  status: string;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800",
  active: "bg-green-100 text-green-800",
  completed: "bg-blue-100 text-blue-800",
  archived: "bg-gray-100 text-gray-800",
};

export default function BriefsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState("");
  const [clientName, setClientName] = useState("");
  const [projectType, setProjectType] = useState("product_visualization");
  const [objective, setObjective] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["briefs", orgId],
    queryFn: () =>
      apiWithAuth<{ data: ClientBrief[]; meta: { total: number } }>(
        `/orgs/${orgId}/briefs`,
      ),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/briefs`, {
        method: "POST",
        body: JSON.stringify({
          title,
          client_name: clientName,
          project_type: projectType,
          objective,
        }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["briefs", orgId] });
      setShowCreate(false);
      setTitle("");
      setClientName("");
      setObjective("");
    },
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Client Briefs</h1>
        <Button onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? "Cancel" : "+ New Brief"}
        </Button>
      </div>

      {showCreate && (
        <div className="mb-6 rounded-lg border p-4">
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Brief title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
            />
            <input
              type="text"
              placeholder="Client name"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
            />
            <select
              value={projectType}
              onChange={(e) => setProjectType(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
            >
              <option value="product_visualization">Product Visualization</option>
              <option value="social_media">Social Media</option>
              <option value="brand_identity">Brand Identity</option>
              <option value="video_production">Video Production</option>
              <option value="other">Other</option>
            </select>
            <textarea
              placeholder="Objective — what does the client want?"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm"
              rows={3}
            />
            <Button
              onClick={() => createMutation.mutate()}
              disabled={
                !title.trim() || !clientName.trim() || !objective.trim() || createMutation.isPending
              }
            >
              Create Brief
            </Button>
          </div>
        </div>
      )}

      {isLoading ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading briefs...</p>
      ) : !data?.data.length ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No client briefs yet. Create one to start a commercial production project.
        </p>
      ) : (
        <div className="space-y-3">
          {data.data.map((brief) => (
            <Link
              key={brief.id}
              href={`/dashboard/orgs/${orgId}/briefs/${brief.id}`}
              className="flex items-center justify-between rounded-lg border p-4 transition-shadow hover:shadow-md"
            >
              <div>
                <h3 className="font-semibold">{brief.title}</h3>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  {brief.client_name} · {brief.project_type.replace("_", " ")}
                </p>
              </div>
              <span
                className={`rounded-full px-2 py-0.5 text-xs capitalize ${STATUS_COLORS[brief.status] || ""}`}
              >
                {brief.status}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
