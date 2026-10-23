import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SsoProviderList } from "@/components/sso-provider-list";

describe("SsoProviderList", () => {
  it("renders providers", () => {
    const { container } = render(
      <SsoProviderList active={2} onAdd={vi.fn()} onToggle={vi.fn()}
        providers={[
          { name: "Google", protocol: "oauth2", status: "active" },
          { name: "Okta", protocol: "saml", status: "active" },
          { name: "Legacy", protocol: "oidc", status: "disabled" },
        ]} />
    );
    expect(container.textContent).toContain("SSO Providers");
    expect(container.textContent).toContain("2/3 active");
    expect(container.textContent).toContain("Google");
    expect(container.textContent).toContain("oauth2");
    expect(container.textContent).toContain("Okta");
    expect(container.textContent).toContain("saml");
    expect(container.textContent).toContain("Disabled");
  });
});
