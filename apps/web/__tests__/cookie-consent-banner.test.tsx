import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CookieConsentBanner } from "@/components/cookie-consent-banner";

describe("CookieConsentBanner", () => {
  it("renders banner", () => {
    const onAccept = vi.fn();
    const { container, getByText } = render(
      <CookieConsentBanner onAcceptAll={onAccept} onRejectAll={vi.fn()} onSave={vi.fn()}
        categories={[
          { id: "necessary", label: "Necessary", description: "", required: true, defaultVal: true },
          { id: "analytics", label: "Analytics", description: "", required: false, defaultVal: false },
        ]} />
    );
    expect(container.textContent).toContain("Cookie Preferences");
    expect(container.textContent).toContain("Necessary");
    expect(container.textContent).toContain("Analytics");
    fireEvent.click(getByText("Accept All"));
    expect(onAccept).toHaveBeenCalled();
  });
});
