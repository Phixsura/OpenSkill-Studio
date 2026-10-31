import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDruidPanel } from "@/components/fleet-druid-panel";
describe("FleetDruidPanel", () => { it("renders", () => {
    const { container } = render(<FleetDruidPanel clusters={3} healthy={3} segments={150000} qps={15000} />);
    expect(container.textContent).toContain("Druid");
}); });
