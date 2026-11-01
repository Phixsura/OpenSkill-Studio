import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSchedLatPanel } from "@/components/fleet-sched-lat-panel";
describe("FleetSchedLatPanel", () => { it("renders", () => {
    const { container } = render(<FleetSchedLatPanel total={50} avgMs={1200} slowScheduling={3} fast={false} />);
    expect(container.textContent).toContain("Scheduling Latency");
    expect(container.textContent).toContain("3 slow");
}); });
