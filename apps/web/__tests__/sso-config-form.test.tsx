import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SsoConfigForm } from "@/components/sso-config-form";

describe("SsoConfigForm", () => {
  const providers = [
    { id: "oidc", label: "OpenID Connect", fields: ["issuer_url", "client_id", "client_secret"] },
    { id: "saml", label: "SAML 2.0", fields: ["metadata_url", "entity_id"] },
  ];
  it("renders", () => {
    const { container } = render(<SsoConfigForm providers={providers} onSave={vi.fn()} />);
    expect(container.textContent).toContain("SSO Configuration");
    expect(container.textContent).toContain("OpenID Connect");
    expect(container.textContent).toContain("SAML 2.0");
    expect(container.querySelectorAll("input").length).toBe(3); // oidc fields
    expect(container.textContent).toContain("Save Configuration");
  });
});
