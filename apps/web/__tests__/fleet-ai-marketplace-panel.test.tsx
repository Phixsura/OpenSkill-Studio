import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMarketplacePanel } from "@/components/fleet-ai-marketplace-panel";
describe("FleetAiMarketplacePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMarketplacePanel marketplaces={3} active={3} listings={1000} installs={200000} />);
    expect(container.textContent).toContain("AI Marketplace");
}); });
