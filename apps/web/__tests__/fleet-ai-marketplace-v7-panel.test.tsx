import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMarketplaceV7Panel } from "@/components/fleet-ai-marketplace-v7-panel";
describe("FleetAiMarketplaceV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMarketplaceV7Panel marketplaces={3} active={3} listings={100000} downloads={50000000} publishers={20000} revenue={200000000} />);
    expect(container.textContent).toContain("Marketplace v7");
}); });
