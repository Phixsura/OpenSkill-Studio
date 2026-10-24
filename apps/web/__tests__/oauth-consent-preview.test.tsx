import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OAuthConsentPreview } from "@/components/oauth-consent-preview";

describe("OAuthConsentPreview", () => {
  it("renders consent screen", () => {
    const { container } = render(
      <OAuthConsentPreview appName="MyApp" scopes={["read", "write"]} redirectUri="https://app.com/callback" onApprove={vi.fn()} onDeny={vi.fn()} />
    );
    expect(container.textContent).toContain("MyApp wants to access");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
    expect(container.textContent).toContain("app.com");
  });
  it("calls onApprove", () => {
    const fn = vi.fn();
    const { container } = render(
      <OAuthConsentPreview appName="X" scopes={[]} redirectUri="https://x.com" onApprove={fn} onDeny={vi.fn()} />
    );
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Authorize")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalled();
  });
});
