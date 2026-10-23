import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SsoProviderList } from "@/components/sso-provider-list";

describe("SsoProviderList", () => {
  it("renders providers", () => {
    const onToggle = vi.fn();
    const { container, getAllByRole } = render(
      <SsoProviderList onToggle={onToggle} providers={[
        { id: "okta1", name: "Acme Okta", protocol: "saml", domains: ["acme.com"], enabled: true, verified: true },
        { id: "azure1", name: "Azure AD", protocol: "oidc", domains: ["corp.com"], enabled: false, verified: false },
      ]} />
    );
    expect(container.textContent).toContain("SSO Providers");
    expect(container.textContent).toContain("Acme Okta");
    expect(container.textContent).toContain("saml");
    expect(container.textContent).toContain("Verified");
    expect(container.textContent).toContain("Azure AD");
    const buttons = getAllByRole("button");
    fireEvent.click(buttons[0]);
    expect(onToggle).toHaveBeenCalledWith("okta1");
  });
});
