import "server-only";

import { headers } from "next/headers";

const API_BASE = process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "";

export interface SiteBranding {
  product_display_name: string | null;
  logo_key: string | null;
  favicon_key: string | null;
  login_tagline: string | null;
  theme_tokens: Record<string, string>;
  legal_links: { label: string; url: string }[];
  support_email: string | null;
  support_url: string | null;
}

export interface SiteContext {
  tenant_id: string | null;
  branding: SiteBranding | null;
}

const RADIUS_MAP: Record<string, string> = {
  none: "0rem",
  sm: "0.25rem",
  md: "0.5rem",
  lg: "0.75rem",
  full: "9999px",
};

/** Convert "#RRGGBB" to the "H S% L%" triple our CSS variables expect. */
function hexToHslTriple(hex: string): string | null {
  const m = /^#([0-9a-fA-F]{6})$/.exec(hex);
  const digits = m?.[1];
  if (!digits) return null;
  const r = parseInt(digits.slice(0, 2), 16) / 255;
  const g = parseInt(digits.slice(2, 4), 16) / 255;
  const b = parseInt(digits.slice(4, 6), 16) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  let h = 0;
  let s = 0;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) h = ((b - r) / d + 2) / 6;
    else h = ((r - g) / d + 4) / 6;
  }
  return `${Math.round(h * 360)} ${Math.round(s * 1000) / 10}% ${Math.round(l * 1000) / 10}%`;
}

/** Resolve white-label site context for the current request's host.
 * Platform hosts (no x-tenant-host header) short-circuit to null. */
export async function getSiteContext(): Promise<SiteContext | null> {
  const headerList = await headers();
  const tenantHost = headerList.get("x-tenant-host");
  if (!tenantHost || !API_BASE) return null;
  try {
    const res = await fetch(
      `${API_BASE}/api/v1/public/site-context?host=${encodeURIComponent(tenantHost)}`,
      { next: { revalidate: 300 } },
    );
    if (!res.ok) return null;
    const body = await res.json();
    return body?.data ?? null;
  } catch {
    return null; // white-label resolution is best-effort — never break the app
  }
}

/** Build a CSS-variable override string from validated theme tokens.
 * Tokens arrive server-validated (closed hex/enum set) — hexToHslTriple
 * re-guards anyway so garbage can never reach a style tag. */
export function themeTokensToCss(tokens: Record<string, string>): string {
  const COLOR_KEYS = ["primary", "accent", "background", "foreground", "muted", "border"];
  const parts: string[] = [];
  for (const key of COLOR_KEYS) {
    const triple = tokens[key] ? hexToHslTriple(tokens[key]) : null;
    if (triple) parts.push(`--${key}: ${triple};`);
  }
  if (tokens.radius && RADIUS_MAP[tokens.radius]) {
    parts.push(`--radius: ${RADIUS_MAP[tokens.radius]};`);
  }
  return parts.length ? `:root { ${parts.join(" ")} }` : "";
}
