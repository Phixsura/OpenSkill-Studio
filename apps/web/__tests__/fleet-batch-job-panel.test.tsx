import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBatchJobPanel } from "@/components/fleet-batch-job-panel";
describe("FleetBatchJobPanel", () => { it("renders", () => {
    const { container } = render(<FleetBatchJobPanel total={10} completed={8} failed={2} avgDuration={45} reliable={false} />);
    expect(container.textContent).toContain("Batch Jobs");
    expect(container.textContent).toContain("Job failures");
}); });
