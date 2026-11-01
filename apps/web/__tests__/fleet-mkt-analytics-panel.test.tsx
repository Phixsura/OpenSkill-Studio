import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMktAnalyticsPanel } from "@/components/fleet-mkt-analytics-panel";
describe("FleetMktAnalyticsPanel", () => { it("renders", () => {
    const { container } = render(<FleetMktAnalyticsPanel listings={500} installs={25000} avgRating={4.5} installRate={50} />);
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("25,000 installs");
}); });
