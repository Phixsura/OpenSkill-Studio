import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OAuthScopeSelector } from "@/components/oauth-scope-selector";

describe("OAuthScopeSelector", () => {
  const groups = [{
    category: "user",
    scopes: [{ scope: "read:profile", description: "Read profile", category: "user", risk: "low" }],
  }];
  it("renders", () => {
    const { container } = render(
      <OAuthScopeSelector groups={groups} selected={new Set(["read:profile"])}
        onToggle={vi.fn()} requiresAdminConsent={false} />
    );
    expect(container.textContent).toContain("OAuth Scopes");
    expect(container.textContent).toContain("Read profile");
    expect(container.textContent).toContain("read:profile");
  });
  it("admin consent warning", () => {
    const { container } = render(
      <OAuthScopeSelector groups={groups} selected={new Set()} onToggle={vi.fn()} requiresAdminConsent={true} />
    );
    expect(container.textContent).toContain("admin consent");
  });
});
