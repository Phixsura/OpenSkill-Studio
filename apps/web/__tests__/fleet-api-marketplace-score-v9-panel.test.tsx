import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiMarketplaceScoreV9Panel } from "@/components/fleet-api-marketplace-score-v9-panel";
describe("FleetApiMarketplaceScoreV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiMarketplaceScoreV9Panel />);
    expect(container.textContent).toContain("Marketplace Score v9");
}); });
