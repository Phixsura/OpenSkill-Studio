/** Control-plane shared types + helpers (issue #27, ADR-014 §11.2). */

export interface TenantMembership {
  tenant_id: string;
  slug: string;
  name: string;
  role: string;
  status: string;
}

export interface PartnerMembership {
  partner_id: string;
  name: string;
  role: string;
}

export interface MeExtended {
  id: string;
  email: string;
  display_name: string;
  role: string;
  platform_roles: string[];
  tenant_memberships: TenantMembership[];
  partner_memberships: PartnerMembership[];
  impersonation: { grant_id: string; platform_user_id: string } | null;
}

export interface EntitlementEntry {
  value: unknown;
  source: string;
  enforcement?: string;
  usage?: unknown;
  expires_at?: string | null;
}

export interface TenantEntitlements {
  plan: { key: string; version: number; trial: boolean; trial_ends_at: string | null } | null;
  entitlements: Record<string, EntitlementEntry>;
}

export interface Subscription {
  id: string;
  status: string;
  plan_key: string;
  plan_version: number;
  interval: string;
  currency: string;
  seat_quantity: number;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

export interface InvoiceSummary {
  id: string;
  number: string | null;
  status: string;
  currency: string;
  subtotal_minor: number;
  credit_applied_minor: number;
  total_minor: number;
  amount_due_minor: number;
  issued_at: string | null;
  due_at: string | null;
}

export interface InvoiceLine {
  id: string;
  line_type: string;
  description: string;
  quantity: string;
  unit_amount_minor: number;
  amount_minor: number;
  usage_summary: Record<string, unknown> | null;
}

/** Zero-decimal currencies bill in whole units (mirror of backend CURRENCY_MINOR). */
const ZERO_DECIMAL = new Set(["JPY", "KRW"]);

/** Format integer minor units as a display amount ("$199.00", "¥1,500"). */
export function formatMinor(amountMinor: number, currency: string): string {
  const divisor = ZERO_DECIMAL.has(currency) ? 1 : 100;
  const value = amountMinor / divisor;
  try {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
      minimumFractionDigits: ZERO_DECIMAL.has(currency) ? 0 : 2,
    }).format(value);
  } catch {
    return `${currency} ${value.toFixed(ZERO_DECIMAL.has(currency) ? 0 : 2)}`;
  }
}

/** Parse a user-typed major-unit amount into integer minor units for the
 * given currency (R101: hardcoded *100 broke zero-decimal currencies by 100x).
 * Returns null when the input is not a finite positive-or-zero number. */
export function majorToMinor(input: string, currency: string): number | null {
  const value = parseFloat(input);
  if (!Number.isFinite(value)) return null;
  const factor = ZERO_DECIMAL.has(currency) ? 1 : 100;
  return Math.round(value * factor);
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  trial: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  past_due: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  suspended: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  cancelled: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  archived: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  open: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  paid: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  draft: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  void: "bg-gray-100 text-gray-500 line-through dark:bg-gray-800",
  finalized: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  approved: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  paid_externally: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  pending_verification: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  verified: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  disabled: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  running: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  // R101[L15]: statuses the backend actually emits but the map missed — they
  // all fell through to neutral gray, hiding warning/error states in every
  // badge (subscription, invoice, purchase, reservation, rated-usage).
  cancel_at_period_end: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  uncollectible: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  pending: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  refunded: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  held: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
  settled: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  released: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  expired: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  rated: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  invoiced: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  blocked: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  voided: "bg-gray-100 text-gray-500 line-through dark:bg-gray-800",
};

export function StatusBadgeClass(status: string): string {
  return STATUS_COLORS[status] ?? "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";
}
