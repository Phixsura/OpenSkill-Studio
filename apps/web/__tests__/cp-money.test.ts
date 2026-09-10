// P11: control-plane money display helpers (#27 §11.3)
import { describe, expect, it } from "vitest";

import { formatMinor, majorToMinor, StatusBadgeClass } from "@/lib/cp";

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
