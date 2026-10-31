import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHoneycombPanel } from "@/components/fleet-honeycomb-panel";
describe("FleetHoneycombPanel", () => { it("renders", () => {
    const { container } = render(<FleetHoneycombPanel datasets={10} active={10} eventsPerSec={50000} queries={2000} />);
    expect(container.textContent).toContain("Honeycomb");
    expect(container.textContent).toContain("50,000 eps");
}); });
