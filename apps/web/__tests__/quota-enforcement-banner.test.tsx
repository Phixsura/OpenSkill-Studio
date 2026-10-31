import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuotaEnforcementBanner } from "@/components/quota-enforcement-banner";

describe("QuotaEnforcementBanner", () => {
  it("renders blocked", () => {
    const results = [{ action: "block", resource: "API Calls", message: "Quota exceeded" }];
    const { container } = render(<QuotaEnforcementBanner results={results} onUpgrade={vi.fn()} />);
    expect(container.textContent).toContain("🚫 API Calls quota exceeded");
    expect(container.textContent).toContain("Upgrade");
  });
  it("renders warned", () => {
    const results = [{ action: "warn", resource: "Storage", message: "Grace period" }];
    const { container } = render(<QuotaEnforcementBanner results={results} onUpgrade={vi.fn()} />);
    expect(container.textContent).toContain("⚠️ Storage approaching limit");
  });
  it("returns null when ok", () => {
    const results = [{ action: "allow", resource: "API" }];
    const { container } = render(<QuotaEnforcementBanner results={results} onUpgrade={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });
});
