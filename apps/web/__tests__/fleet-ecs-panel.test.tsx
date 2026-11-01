import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEcsPanel } from "@/components/fleet-ecs-panel";
describe("FleetEcsPanel", () => { it("renders", () => {
    const { container } = render(<FleetEcsPanel services={20} active={20} runningTasks={100} desiredTasks={100} stable={true} />);
    expect(container.textContent).toContain("ECS");
    expect(container.textContent).toContain("100/100");
}); });
