import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFargatePanel } from "@/components/fleet-fargate-panel";
describe("FleetFargatePanel", () => { it("renders", () => {
    const { container } = render(<FleetFargatePanel totalTasks={50} running={50} cpuUnits={12800} memoryMb={25600} />);
    expect(container.textContent).toContain("Fargate");
}); });
