import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPlausiblePanel } from "@/components/fleet-plausible-panel";
describe("FleetPlausiblePanel", () => { it("renders", () => {
    const { container } = render(<FleetPlausiblePanel sites={20} active={20} pageviews={5000000} visitors={1000000} />);
    expect(container.textContent).toContain("Plausible");
    expect(container.textContent).toContain("1,000,000");
}); });
