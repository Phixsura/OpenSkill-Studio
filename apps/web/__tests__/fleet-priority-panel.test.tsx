import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPriorityPanel } from "@/components/fleet-priority-panel";
describe("FleetPriorityPanel", () => { it("renders", () => {
    const { container } = render(<FleetPriorityPanel total={20} noPriority={5} allPrioritized={false} />);
    expect(container.textContent).toContain("Pod Priority");
    expect(container.textContent).toContain("5 using default");
}); });
