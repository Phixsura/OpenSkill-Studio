import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTaskQueueV9Panel } from "@/components/fleet-task-queue-v9-panel";
describe("FleetTaskQueueV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTaskQueueV9Panel queues={10} workers={100} />);
    expect(container.textContent).toContain("Task Queue v9");
}); });
