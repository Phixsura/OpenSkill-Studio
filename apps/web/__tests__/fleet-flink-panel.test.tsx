import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFlinkPanel } from "@/components/fleet-flink-panel";
describe("FleetFlinkPanel", () => { it("renders", () => {
    const { container } = render(<FleetFlinkPanel clusters={3} running={3} taskSlots={96} checkpointsOk={true} />);
    expect(container.textContent).toContain("Flink");
    expect(container.textContent).toContain("96 slots");
}); });
