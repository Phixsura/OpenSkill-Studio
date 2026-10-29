import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiSSOProviderCard from "../src/components/api-developer-platform-sdk-api-developer-api-sso-provider-card";

const providers = [
  { provider_id: "google", provider_type: "oidc", issuer_url: "https://accounts.google.com", enabled: true, login_count: 5000 },
  { provider_id: "okta", provider_type: "saml", issuer_url: "https://acme.okta.com", enabled: false, login_count: 200 },
];

describe("Card", () => {
  it("shows SSO providers", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiSSOProviderCard providers={providers} appName="App" />);
    expect(container.textContent).toContain("SSO Providers");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("oidc");
    expect(container.textContent).toContain("google");
    expect(container.textContent).toContain("5000 logins");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiSSOProviderCard providers={[]} appName="App" />);
    expect(container.textContent).toContain("No SSO providers");
  });
});
