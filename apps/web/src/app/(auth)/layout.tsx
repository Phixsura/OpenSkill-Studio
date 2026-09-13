import Link from "next/link";

import { getSiteContext } from "@/lib/site-context";

export default async function AuthLayout({ children }: { children: React.ReactNode }) {
  // White-label: custom domains show the tenant's name/tagline/legal links
  const site = await getSiteContext();
  const branding = site?.branding ?? null;
  const displayName = branding?.product_display_name || "OpenSkill Studio";

  return (
    <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--secondary))]">
      <div className="w-full max-w-md space-y-6 rounded-lg border bg-[hsl(var(--card))] p-8 shadow-sm">
        <div className="text-center">
          <Link href="/" className="text-xl font-bold tracking-tight">
            {displayName}
          </Link>
          {branding?.login_tagline && (
            <p className="mt-1 text-sm text-[hsl(var(--muted-foreground))]">
              {branding.login_tagline}
            </p>
          )}
        </div>
        {children}
        {branding && branding.legal_links.length > 0 && (
          <div className="flex flex-wrap justify-center gap-3 border-t pt-4 text-xs text-[hsl(var(--muted-foreground))]">
            {branding.legal_links.map((link) => (
              <a
                key={link.url}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline"
              >
                {link.label}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
