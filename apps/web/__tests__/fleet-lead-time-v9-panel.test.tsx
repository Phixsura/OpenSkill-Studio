import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLeadTimeV9Panel } from "@/components/fleet-lead-time-v9-panel";
describe("FleetLeadTimeV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLeadTimeV9Panel changes={500} avgMin={17} />);
    expect(container.textContent).toContain("Lead Time v9");
}); });
