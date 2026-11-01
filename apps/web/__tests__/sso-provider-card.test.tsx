import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SSOProviderCard from "../src/components/sso-provider-card";

const providers = [
  {
    provider_id: "okta",
    provider_type: "oidc",
    name: "Okta",
    issuer_url: "https://okta.com",
    enabled: true,
    success_rate: 99.5,
    auth_count: 500,
  },
  {
    provider_id: "azure",
    provider_type: "saml",
    name: "Azure AD",
    issuer_url: "https://login.microsoft.com",
    enabled: false,
    success_rate: 100,
    auth_count: 0,
  },
];

describe("SSOProviderCard", () => {
  it("renders header and enabled count", () => {
    const { container } = render(<SSOProviderCard providers={providers} appName="App" />);
    expect(container.textContent).toContain("SSO Providers");
    expect(container.textContent).toContain("1/2 enabled");
  });

  it("shows provider names and types", () => {
    const { container } = render(<SSOProviderCard providers={providers} appName="App" />);
    expect(container.textContent).toContain("Okta");
    expect(container.textContent).toContain("OIDC");
    expect(container.textContent).toContain("Azure AD");
    expect(container.textContent).toContain("SAML");
  });

  it("shows success rate and auth count", () => {
    const { container } = render(<SSOProviderCard providers={providers} appName="App" />);
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("500 auths");
  });

  it("shows empty state", () => {
    const { container } = render(<SSOProviderCard providers={[]} appName="App" />);
    expect(container.textContent).toContain("No SSO providers");
  });
});
