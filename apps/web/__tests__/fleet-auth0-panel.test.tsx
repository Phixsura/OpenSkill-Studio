import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAuth0Panel } from "@/components/fleet-auth0-panel";
describe("FleetAuth0Panel", () => { it("renders", () => {
    const { container } = render(<FleetAuth0Panel tenants={5} active={5} logins={5000000} mfaPct={90} />);
    expect(container.textContent).toContain("Auth0");
    expect(container.textContent).toContain("90% MFA");
}); });
