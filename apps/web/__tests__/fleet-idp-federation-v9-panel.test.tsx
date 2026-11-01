import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIdpFederationV9Panel } from "@/components/fleet-idp-federation-v9-panel";
describe("FleetIdpFederationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIdpFederationV9Panel providers={5} connected={5} />);
    expect(container.textContent).toContain("IdP Federation v9");
}); });
