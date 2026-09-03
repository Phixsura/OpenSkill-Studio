// P11: control-plane money display helpers (#27 §11.3)
import { describe, expect, it } from "vitest";

import { formatMinor, StatusBadgeClass } from "@/lib/cp";

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
});

describe("StatusBadgeClass", () => {
  it("maps known statuses and falls back for unknown ones", () => {
    expect(StatusBadgeClass("active")).toContain("green");
    expect(StatusBadgeClass("past_due")).toContain("amber");
    expect(StatusBadgeClass("definitely_not_a_status")).toContain("gray");
  });
});
