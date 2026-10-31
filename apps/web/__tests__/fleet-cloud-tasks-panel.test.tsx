import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudTasksPanel } from "@/components/fleet-cloud-tasks-panel";
describe("FleetCloudTasksPanel", () => { it("renders", () => {
    const { container } = render(<FleetCloudTasksPanel queues={10} active={10} tasks={5000000} successRate={99.9} />);
    expect(container.textContent).toContain("Cloud Tasks");
}); });
