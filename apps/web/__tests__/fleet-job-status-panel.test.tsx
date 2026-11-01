import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetJobStatusPanel } from "@/components/fleet-job-status-panel";
describe("FleetJobStatusPanel", () => { it("renders", () => {
    const { container } = render(<FleetJobStatusPanel total={4} succeeded={2} failed={1} running={1} successRate={50} />);
    expect(container.textContent).toContain("Fleet Jobs");
    expect(container.textContent).toContain("50% success");
}); });
