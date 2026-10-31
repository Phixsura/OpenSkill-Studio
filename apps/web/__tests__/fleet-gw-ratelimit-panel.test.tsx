import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGwRatelimitPanel } from "@/components/fleet-gw-ratelimit-panel";
describe("FleetGwRatelimitPanel", () => { it("renders", () => {
    const { container } = render(<FleetGwRatelimitPanel limited={150} total={1500} limitedPct={10} excessive={true} />);
    expect(container.textContent).toContain("Gateway Rate Limits");
    expect(container.textContent).toContain("Excessive");
}); });
