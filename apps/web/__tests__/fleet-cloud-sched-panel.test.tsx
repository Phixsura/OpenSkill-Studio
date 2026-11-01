import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudSchedPanel } from "@/components/fleet-cloud-sched-panel";
describe("FleetCloudSchedPanel", () => { it("renders", () => {
    const { container } = render(<FleetCloudSchedPanel jobs={20} enabled={20} executions={2000} failed={0} />);
    expect(container.textContent).toContain("Cloud Scheduler");
}); });
