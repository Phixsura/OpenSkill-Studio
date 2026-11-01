import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVpaPanel } from "@/components/fleet-vpa-panel";
describe("FleetVpaPanel", () => { it("renders", () => {
    const { container } = render(<FleetVpaPanel total={10} autoMode={7} monthlySavings={3500} effective={true} />);
    expect(container.textContent).toContain("VPA");
    expect(container.textContent).toContain("Saving costs");
}); });
