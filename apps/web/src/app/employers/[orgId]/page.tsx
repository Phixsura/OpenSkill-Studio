"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

interface CareerPageData {
  profile: {
    org_id: string;
    company_size: string | null;
    industry: string | null;
    website_url: string | null;
    logo_url: string | null;
    description: string | null;
    cover_image_url: string | null;
    culture_text: string | null;
    benefits: string[];
    values: string[];
    social_links: Record<string, string>;
    verification_status: string;
  };
  opportunities: {
    id: string;
    title: string;
    opportunity_type: string;
    location_mode: string | null;
    location_text: string | null;
    compensation_display: string | null;
    openings: number;
    application_deadline: string | null;
  }[];
}

const TYPE_LABELS: Record<string, string> = {
  internship: "Internship",
  full_time: "Full-Time",
  part_time: "Part-Time",
  contract: "Contract",
  freelance: "Freelance",
  project_role: "Project Role",
  apprenticeship: "Apprenticeship",
  campus_project: "Campus Project",
};

export default function EmployerCareerPage() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["career-page", orgId],
    queryFn: () => api<{ data: CareerPageData }>(`/talent/employers/${orgId}/career-page`),
    enabled: !!orgId,
  });

  if (isLoading) {
    if (isError) return <div className="p-8 text-center text-red-600">Failed to load data</div>;

  return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <div className="text-[hsl(var(--muted-foreground))]">Loading…</div>
      </div>
    );
  }

  if (error || !data?.data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <div className="rounded-lg border bg-[hsl(var(--card))] p-8 text-center">
          <div className="mb-4 text-4xl">🏢</div>
          <h1 className="mb-2 text-xl font-bold">Employer Not Found</h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            This employer page doesn&apos;t exist or is not available.
          </p>
        </div>
      </div>
    );
  }

  const { profile, opportunities } = data.data;

  return (
    <div className="min-h-screen bg-[hsl(var(--background))]">
      {/* Cover / Header */}
      {profile.cover_image_url && (
        <div className="h-48 w-full overflow-hidden bg-[hsl(var(--secondary))]">
          <img src={profile.cover_image_url} alt="" className="h-full w-full object-cover" />
        </div>
      )}

      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* Company Info */}
        <div className="mb-8 flex items-start gap-4">
          {profile.logo_url && (
            <img
              src={profile.logo_url}
              alt=""
              className="h-16 w-16 rounded-lg border object-cover"
            />
          )}
          <div>
            <h1 className="text-2xl font-bold">{profile.org_id}</h1>
            <div className="mt-1 flex flex-wrap gap-3 text-sm text-[hsl(var(--muted-foreground))]">
              {profile.industry && <span>{profile.industry}</span>}
              {profile.company_size && <span>· {profile.company_size}</span>}
              {profile.verification_status === "verified" && (
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                  ✓ Verified
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Description */}
        {profile.description && (
          <div className="mb-8 rounded-lg border bg-[hsl(var(--card))] p-6 shadow-sm">
            <h2 className="mb-3 text-lg font-semibold">About</h2>
            <p className="whitespace-pre-wrap text-[hsl(var(--muted-foreground))]">
              {profile.description}
            </p>
          </div>
        )}

        {/* Culture */}
        {profile.culture_text && (
          <div className="mb-8 rounded-lg border bg-[hsl(var(--card))] p-6 shadow-sm">
            <h2 className="mb-3 text-lg font-semibold">Culture</h2>
            <p className="whitespace-pre-wrap text-[hsl(var(--muted-foreground))]">
              {profile.culture_text}
            </p>
          </div>
        )}

        {/* Benefits & Values */}
        <div className="mb-8 grid gap-6 sm:grid-cols-2">
          {profile.benefits.length > 0 && (
            <div className="rounded-lg border bg-[hsl(var(--card))] p-6 shadow-sm">
              <h2 className="mb-3 text-lg font-semibold">Benefits</h2>
              <ul className="space-y-2">
                {profile.benefits.map((b, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]"
                  >
                    <span className="text-green-500">✓</span> {b}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {profile.values.length > 0 && (
            <div className="rounded-lg border bg-[hsl(var(--card))] p-6 shadow-sm">
              <h2 className="mb-3 text-lg font-semibold">Values</h2>
              <ul className="space-y-2">
                {profile.values.map((v, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]"
                  >
                    <span className="text-blue-500">◆</span> {v}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Open Opportunities */}
        <div className="mb-8">
          <h2 className="mb-4 text-lg font-semibold">Open Positions ({opportunities.length})</h2>
          {opportunities.length === 0 ? (
            <div className="rounded-lg border bg-[hsl(var(--card))] p-8 text-center text-[hsl(var(--muted-foreground))]">
              No open positions at this time.
            </div>
          ) : (
            <div className="space-y-4">
              {opportunities.map((opp) => (
                <a
                  key={opp.id}
                  href={`/dashboard/opportunities/${opp.id}`}
                  className="block rounded-lg border bg-[hsl(var(--card))] p-5 shadow-sm transition-colors hover:border-[hsl(var(--primary))]"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium">{opp.title}</h3>
                      <div className="mt-1 flex flex-wrap gap-2 text-sm text-[hsl(var(--muted-foreground))]">
                        <span className="rounded-full bg-[hsl(var(--secondary))] px-2 py-0.5 text-xs">
                          {TYPE_LABELS[opp.opportunity_type] || opp.opportunity_type}
                        </span>
                        {opp.location_mode && (
                          <span>
                            {opp.location_mode === "remote"
                              ? "🌐 Remote"
                              : opp.location_mode === "hybrid"
                                ? "🏢 Hybrid"
                                : "📍 On-site"}
                          </span>
                        )}
                        {opp.location_text && <span>{opp.location_text}</span>}
                      </div>
                    </div>
                    {opp.compensation_display && (
                      <span className="text-sm font-medium text-[hsl(var(--muted-foreground))]">
                        {opp.compensation_display}
                      </span>
                    )}
                  </div>
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Social Links */}
        {Object.keys(profile.social_links).length > 0 && (
          <div className="text-center text-sm text-[hsl(var(--muted-foreground))]">
            {profile.social_links.website && (
              <a
                href={profile.social_links.website}
                className="mx-2 underline hover:text-[hsl(var(--foreground))]"
                target="_blank"
                rel="noopener noreferrer"
              >
                Website
              </a>
            )}
            {profile.social_links.linkedin && (
              <a
                href={profile.social_links.linkedin}
                className="mx-2 underline hover:text-[hsl(var(--foreground))]"
                target="_blank"
                rel="noopener noreferrer"
              >
                LinkedIn
              </a>
            )}
            {profile.social_links.twitter && (
              <a
                href={profile.social_links.twitter}
                className="mx-2 underline hover:text-[hsl(var(--foreground))]"
                target="_blank"
                rel="noopener noreferrer"
              >
                Twitter
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
