import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetUnleashPanel } from "@/components/fleet-unleash-panel";
describe("FleetUnleashPanel", () => { it("renders", () => {
    const { container } = render(<FleetUnleashPanel total={80} enabled={60} stale={5} impressions={500000} />);
    expect(container.textContent).toContain("Unleash");
    expect(container.textContent).toContain("500,000");
}); });
