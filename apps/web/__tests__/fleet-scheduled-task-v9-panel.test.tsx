import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetScheduledTaskV9Panel } from "@/components/fleet-scheduled-task-v9-panel";
describe("FleetScheduledTaskV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetScheduledTaskV9Panel total={200} onTime={198} />);
    expect(container.textContent).toContain("Scheduled Task v9");
}); });
