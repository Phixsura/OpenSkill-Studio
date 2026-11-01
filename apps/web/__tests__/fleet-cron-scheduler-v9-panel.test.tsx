import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCronSchedulerV9Panel } from "@/components/fleet-cron-scheduler-v9-panel";
describe("FleetCronSchedulerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCronSchedulerV9Panel jobs={100} running={5} />);
    expect(container.textContent).toContain("Cron Scheduler v9");
}); });
