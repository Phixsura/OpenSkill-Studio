import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetJobSchedulerV9Panel } from "@/components/fleet-job-scheduler-v9-panel";
describe("FleetJobSchedulerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetJobSchedulerV9Panel total={100} running={10} />);
    expect(container.textContent).toContain("Job Scheduler v9");
}); });
