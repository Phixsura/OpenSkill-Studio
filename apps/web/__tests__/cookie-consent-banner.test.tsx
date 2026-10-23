import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CookieConsentBanner } from "@/components/cookie-consent-banner";

describe("CookieConsentBanner", () => {
  const categories = {
    essential: { label: "Essential", required: true, description: "Required" },
    analytics: { label: "Analytics", required: false, description: "Usage data" },
  };
  it("renders banner", () => {
    const { container } = render(<CookieConsentBanner categories={categories} onAcceptAll={vi.fn()} onSave={vi.fn()} />);
    expect(container.textContent).toContain("Cookie Preferences");
    expect(container.textContent).toContain("Accept All");
  });
  it("accept all", () => {
    const fn = vi.fn();
    const { container } = render(<CookieConsentBanner categories={categories} onAcceptAll={fn} onSave={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Accept All")!);
    expect(fn).toHaveBeenCalled();
  });
  it("shows customize", () => {
    const { container } = render(<CookieConsentBanner categories={categories} onAcceptAll={vi.fn()} onSave={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Customize")!);
    expect(container.textContent).toContain("Essential");
    expect(container.textContent).toContain("Analytics");
  });
});
