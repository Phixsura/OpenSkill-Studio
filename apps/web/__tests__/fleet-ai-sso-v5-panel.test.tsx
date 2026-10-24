import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSsoV5Panel } from "@/components/fleet-ai-sso-v5-panel";
describe("FleetAiSsoV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSsoV5Panel providers={3} active={3} logins={5000000} protocols={["SAML", "OIDC"]} mfa={true} />);
    expect(container.textContent).toContain("SSO v5");
}); });
