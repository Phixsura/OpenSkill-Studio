import type { Metadata } from "next";

import VerifyPassportClient from "./verify-client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface Props {
  params: Promise<{ token: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { token } = await params;

  // Attempt to fetch snapshot info for dynamic metadata
  // This is a public endpoint — no auth needed
  let title = "Verified Skill Passport — OpenSkill Studio";
  let description = "View a verified skill passport from OpenSkill Studio.";

  try {
    const res = await fetch(`${API_BASE}/api/v1/verify/passport/${token}`, {
      next: { revalidate: 60 },
    });
    if (res.ok) {
      const data = await res.json();
      if (data.data?.status === "active") {
        const capCount = data.data.payload?.capabilities?.length ?? 0;
        title = `Verified Skill Passport — ${capCount} Capabilities`;
        description = `A verified skill passport with ${capCount} verified capabilities from OpenSkill Studio.`;
      } else if (data.data?.status === "revoked") {
        title = "Passport Revoked — OpenSkill Studio";
        description = "This skill passport snapshot has been revoked by its owner.";
      } else if (data.data?.status === "expired") {
        title = "Passport Expired — OpenSkill Studio";
        description = "This skill passport snapshot has expired.";
      }
    }
  } catch {
    // Fail silently — metadata is best-effort
  }

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      siteName: "OpenSkill Studio",
      type: "website",
    },
    twitter: {
      card: "summary",
      title,
      description,
    },
    robots: {
      index: true,
      follow: false, // Don't follow links from passport pages
    },
  };
}

export default function VerifyPassportPage() {
  return <VerifyPassportClient />;
}
