// P11: control-plane money display helpers (#27 §11.3)
import { describe, expect, it } from "vitest";

import { STATUS_COLORS, formatMinor, majorToMinor, StatusBadgeClass } from "@/lib/cp";

describe("formatMinor", () => {
  it("formats standard 2-decimal currencies from minor units", () => {
    expect(formatMinor(19900, "USD")).toBe("$199.00");
    expect(formatMinor(0, "USD")).toBe("$0.00");
    expect(formatMinor(1, "USD")).toBe("$0.01");
  });

  it("handles negatives (credits / refunds)", () => {
    expect(formatMinor(-13267, "USD")).toBe("-$132.67");
  });

  it("treats zero-decimal currencies as whole units", () => {
    // JPY minor multiplier is 1 — 1500 minor = ¥1,500, not ¥15.00
    expect(formatMinor(1500, "JPY")).toBe("¥1,500");
    expect(formatMinor(1500, "KRW")).toBe("₩1,500");
  });

  it("never throws on unknown currency codes", () => {
    expect(() => formatMinor(123, "ZZZ")).not.toThrow();
  });

  it("R163: case-insensitive zero-decimal detection (matches backend .upper())", () => {
    // A lowercase code must not miss ZERO_DECIMAL and divide by 100 (100x bug).
    expect(formatMinor(1500, "jpy")).toBe("¥1,500");
    expect(formatMinor(1500, "krw")).toBe("₩1,500");
  });
});

describe("majorToMinor", () => {
  it("converts major units to integer minor per currency", () => {
    expect(majorToMinor("199.00", "USD")).toBe(19900);
    expect(majorToMinor("1500", "JPY")).toBe(1500);
  });

  it("R163: zero-decimal detection is case-insensitive", () => {
    // "1500" jpy must stay 1500 minor, not 150000.
    expect(majorToMinor("1500", "jpy")).toBe(1500);
  });

  it("rejects non-finite input", () => {
    expect(majorToMinor("abc", "USD")).toBeNull();
    expect(majorToMinor("", "USD")).toBeNull();
  });
});

describe("StatusBadgeClass", () => {
  it("maps known statuses and falls back for unknown ones", () => {
    expect(StatusBadgeClass("active")).toContain("green");
    expect(StatusBadgeClass("past_due")).toContain("amber");
    expect(StatusBadgeClass("definitely_not_a_status")).toContain("gray");
  });
});

describe("majorToMinor contract (R298)", () => {
  it("passes NEGATIVE amounts through — signed platform adjustments (clawback)", () => {
    // the docstring once wrongly promised positive-or-zero; the adjust field
    // relies on negatives reaching the API, so this must NOT be null
    expect(majorToMinor("-50.00", "USD")).toBe(-5000);
    expect(majorToMinor("-1500", "JPY")).toBe(-1500);
  });

  it("returns null only for non-finite input", () => {
    expect(majorToMinor("", "USD")).toBeNull();
    expect(majorToMinor("abc", "USD")).toBeNull();
    expect(majorToMinor("1e999", "USD")).toBeNull(); // Infinity
    expect(majorToMinor("NaN", "USD")).toBeNull();
  });

  it("is lenient on trailing junk (parseFloat) — caller must sanitize", () => {
    // documents the real behavior so no caller assumes strict parsing
    expect(majorToMinor("12abc", "USD")).toBe(1200);
  });

  it("rounds to the nearest minor unit at cent precision", () => {
    // Money fields are 2-decimal; sub-cent input is out of spec and left to
    // JS float + the backend's exact Decimal re-validation. At true cent
    // precision the round is unambiguous.
    expect(majorToMinor("0.004", "USD")).toBe(0);
    expect(majorToMinor("0.006", "USD")).toBe(1);
    expect(majorToMinor("2.5", "USD")).toBe(250);
  });
});

describe("StatusBadgeClass coverage (R299)", () => {
  // every status the control-plane UI actually renders through <StatusBadge>
  // must be EXPLICITLY mapped — an unmapped status falls to neutral gray,
  // hiding warning/error/ended states (the R101[L15] recurrence that let a
  // TERMINATED partner and a retired plan version render as plain gray).
  const RENDERED_STATUSES = [
    // tenant.status
    "trial",
    "active",
    "past_due",
    "suspended",
    "cancelled",
    "archived",
    // subscription.status
    "cancel_at_period_end",
    // invoice.status
    "draft",
    "open",
    "finalized",
    "paid",
    "void",
    "uncollectible",
    "refunded",
    // plan version.status
    "retired",
    // partner.status
    "terminated",
    // settlement.status
    "approved",
    "paid_externally",
    // domain.status
    "pending_verification",
    "verified",
    "disabled",
    "failed",
    // reservation / rated-usage
    "held",
    "settled",
    "released",
    "expired",
    "rated",
    "invoiced",
    "blocked",
    "voided",
  ];

  it("maps every rendered status explicitly (no silent fall-through to gray)", () => {
    const missing = RENDERED_STATUSES.filter(
      (st) => !Object.prototype.hasOwnProperty.call(STATUS_COLORS, st),
    );
    expect(missing).toEqual([]);
  });

  it("gives terminated a danger (red) color, not neutral gray", () => {
    expect(StatusBadgeClass("terminated")).toContain("red");
  });

  it("still falls back to gray for a genuinely unknown status", () => {
    expect(StatusBadgeClass("some_future_status_xyz")).toContain("gray");
  });
});

describe("zero-decimal currency set (R300 drift-guard)", () => {
  // ZERO_DECIMAL is maintained independently from the backend's CURRENCY_MINOR
  // (apps/api/app/controlplane/models/pricing.py). Any drift is a 100x money
  // DISPLAY error — the R81/R163 class that recurred twice. The backend test
  // test_zero_decimal_currency_set_frozen_r300 pins the reciprocal; a v1
  // currency addition fires BOTH, forcing the two languages to stay in sync.
  it("is exactly {JPY, KRW} — must match backend CURRENCY_MINOR", () => {
    // JPY/KRW format as whole units; a 2-decimal currency divides by 100
    expect(formatMinor(1500, "JPY")).toBe("¥1,500");
    expect(formatMinor(1500, "KRW")).toBe("₩1,500");
    expect(formatMinor(1500, "USD")).toBe("$15.00");
    expect(formatMinor(1500, "EUR")).toBe("€15.00");
    // a currency NOT in the zero-decimal set must be treated as 2-decimal
    expect(formatMinor(1500, "GBP")).toBe("£15.00");
  });
});

// ── R326: revoked license grants must read as a stop state ──
describe("StatusBadgeClass revoked (R326)", () => {
  it("maps revoked to a danger style, not the neutral fallback", () => {
    const cls = StatusBadgeClass("revoked");
    expect(cls).toContain("red");
    expect(cls).not.toBe(StatusBadgeClass("definitely_unknown_status"));
  });
  it("maps revenue-share entry states (R335), not neutral", () => {
    expect(StatusBadgeClass("accrued")).toContain("blue");
    expect(StatusBadgeClass("adjusted")).toContain("amber");
  });
  it("maps payment success (R328) as green, not neutral", () => {
    expect(StatusBadgeClass("succeeded")).toContain("green");
  });
  it("maps portal review states (R327): action signals are not neutral", () => {
    expect(StatusBadgeClass("revision_requested")).toContain("amber");
    expect(StatusBadgeClass("rejected")).toContain("red");
    expect(StatusBadgeClass("submitted")).toContain("blue");
  });
  it("keeps every stop state visually distinct from neutral gray", () => {
    for (const s of ["revoked", "terminated", "suspended", "failed", "blocked", "rejected"]) {
      expect(STATUS_COLORS[s], s).toBeDefined();
      expect(STATUS_COLORS[s], s).toContain("red");
    }
  });
});
