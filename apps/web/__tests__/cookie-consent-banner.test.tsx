import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CookieConsentBanner } from "@/components/cookie-consent-banner";

describe("CookieConsentBanner", () => {
  const categories = [
    { id: "necessary", label: "Necessary", required: true, description: "Essential", consented: true },
    { id: "analytics", label: "Analytics", required: false, description: "Usage data", consented: false },
  ];
  it("renders banner", () => {
    const { container } = render(
      <CookieConsentBanner categories={categories} domain="example.com"
        onAcceptAll={vi.fn()} onReject={vi.fn()} onCustomize={vi.fn()} />
    );
    expect(container.textContent).toContain("example.com");
    expect(container.textContent).toContain("Necessary");
    expect(container.textContent).toContain("Analytics");
    expect(container.textContent).toContain("Accept All");
  });
  it("accept all", () => {
    const fn = vi.fn();
    const { container } = render(
      <CookieConsentBanner categories={categories} domain="x.com"
        onAcceptAll={fn} onReject={vi.fn()} onCustomize={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Accept All")!);
    expect(fn).toHaveBeenCalled();
  });
});
