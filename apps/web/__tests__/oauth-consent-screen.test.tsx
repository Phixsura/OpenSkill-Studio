import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OAuthConsentScreen } from "@/components/oauth-consent-screen";

const BASE = {
  appName: "Test App", developerName: "Dev Studio",
  scopes: ["read:cohorts", "write:projects"], redirectUri: "https://app.com/callback",
  onApprove: vi.fn(), onDeny: vi.fn(),
};

describe("OAuthConsentScreen", () => {
  it("shows app name", () => {
    const { container } = render(<OAuthConsentScreen {...BASE} />);
    expect(container.textContent).toContain("Test App");
  });

  it("shows developer name", () => {
    const { container } = render(<OAuthConsentScreen {...BASE} />);
    expect(container.textContent).toContain("Dev Studio");
  });

  it("shows scopes with descriptions", () => {
    const { container } = render(<OAuthConsentScreen {...BASE} />);
    expect(container.textContent).toContain("View your cohorts");
  });

  it("shows redirect URI", () => {
    const { container } = render(<OAuthConsentScreen {...BASE} />);
    expect(container.textContent).toContain("app.com/callback");
  });

  it("calls onApprove", () => {
    const onApprove = vi.fn();
    const { container } = render(<OAuthConsentScreen {...BASE} onApprove={onApprove} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Authorize");
    fireEvent.click(btn!);
    expect(onApprove).toHaveBeenCalled();
  });

  it("calls onDeny", () => {
    const onDeny = vi.fn();
    const { container } = render(<OAuthConsentScreen {...BASE} onDeny={onDeny} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Deny");
    fireEvent.click(btn!);
    expect(onDeny).toHaveBeenCalled();
  });
});
