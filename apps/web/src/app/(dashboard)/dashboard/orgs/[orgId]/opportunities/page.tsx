"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { apiWithAuth } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

interface OpenBrief {
  id: string;
  title: string;
  client_name: string;
  project_type: string;
  objective: string;
  status: string;
  created_at: string;
}

const TYPE_LABELS: Record<string, string> = {
  product_visualization: "Product Visualization",
  social_media: "Social Media",
  brand_identity: "Brand Identity",
  video_production: "Video Production",
};

export default function OpportunitiesPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["open-briefs", orgId],
    queryFn: () =>
      apiWithAuth<{ data: OpenBrief[] }>(`/orgs/${orgId}/briefs/open`),
  });

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold">Commercial Opportunities</h1>
      <p className="mb-6 text-sm text-[hsl(var(--muted-foreground))]">
        Open commercial projects you can apply to work on.
      </p>

      {isError && (
        <p className="mb-4 text-sm text-red-600">Failed to load opportunities.</p>
      )}

      {isLoading ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>
      ) : !data?.data.length ? (
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          No open commercial projects at this time. Check back later!
        </p>
      ) : (
        <div className="space-y-4">
          {data.data.map((brief) => (
            <Link
              key={brief.id}
              href={`/dashboard/orgs/${orgId}/briefs/${brief.id}`}
              className="block rounded-lg border p-5 transition-shadow hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold">{brief.title}</h3>
                  <p className="mt-0.5 text-sm text-[hsl(var(--muted-foreground))]">
                    {brief.client_name} ·{" "}
                    {TYPE_LABELS[brief.project_type] || brief.project_type}
                  </p>
                </div>
                <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-800">
                  Open
                </span>
              </div>
              <p className="mt-2 text-sm line-clamp-2">{brief.objective}</p>
              <p className="mt-2 text-xs text-[hsl(var(--muted-foreground))]">
                Posted {new Date(brief.created_at).toLocaleDateString()}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
