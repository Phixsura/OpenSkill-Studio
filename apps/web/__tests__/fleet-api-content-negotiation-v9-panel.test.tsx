import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiContentNegotiationV9Panel } from "@/components/fleet-api-content-negotiation-v9-panel";
describe("FleetApiContentNegotiationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiContentNegotiationV9Panel endpoints={200} json={180} />);
    expect(container.textContent).toContain("Content Negotiation v9");
}); });
