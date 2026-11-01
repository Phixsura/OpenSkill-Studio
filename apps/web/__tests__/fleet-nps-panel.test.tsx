import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNpsPanel } from "@/components/fleet-nps-panel";
describe("FleetNpsPanel", () => { it("renders", () => {
    const { container } = render(<FleetNpsPanel responses={100} nps={60} excellent={true} />);
    expect(container.textContent).toContain("Platform NPS");
    expect(container.textContent).toContain("60");
}); });
