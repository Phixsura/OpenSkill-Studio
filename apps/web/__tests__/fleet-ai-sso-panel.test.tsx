import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSsoPanel } from "@/components/fleet-ai-sso-panel";
describe("FleetAiSsoPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSsoPanel providers={3} active={3} logins={500000} protocols={["SAML", "OIDC"]} mfa={98} />);
    expect(container.textContent).toContain("AI SSO");
}); });
