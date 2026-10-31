import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMktplaceV2Panel } from "@/components/fleet-ai-mktplace-v2-panel";
describe("FleetAiMktplaceV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMktplaceV2Panel marketplaces={3} active={3} listings={10000} publishers={2000} installs={500000} />);
    expect(container.textContent).toContain("Marketplace v2");
}); });
