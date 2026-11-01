import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAspirePanel } from "@/components/fleet-aspire-panel";
describe("FleetAspirePanel", () => { it("renders", () => {
    const { container } = render(<FleetAspirePanel apps={3} running={3} services={15} resources={45} />);
    expect(container.textContent).toContain(".NET Aspire");
    expect(container.textContent).toContain("45 resources");
}); });
