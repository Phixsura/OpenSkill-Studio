import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OAuthScopeSelector } from "@/components/oauth-scope-selector";

describe("OAuthScopeSelector", () => {
  it("renders scopes", () => {
    const { container } = render(
      <OAuthScopeSelector selected={["read:user"]} hasAdmin={false} onToggle={vi.fn()}
        scopes={[
          { scope: "read:user", description: "Read profile", category: "user" },
          { scope: "write:apps", description: "Manage apps", category: "apps" },
          { scope: "admin", description: "Full access", category: "admin" },
        ]} />
    );
    expect(container.textContent).toContain("OAuth Scopes");
    expect(container.textContent).toContain("1 selected");
    expect(container.textContent).toContain("read:user");
    expect(container.textContent).toContain("Read profile");
    expect(container.textContent).toContain("admin");
  });
});
