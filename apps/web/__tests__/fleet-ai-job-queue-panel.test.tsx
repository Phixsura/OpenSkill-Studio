import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiJobQueuePanel } from "@/components/fleet-ai-job-queue-panel";
describe("FleetAiJobQueuePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiJobQueuePanel queues={5} active={5} pending={200} processing={100} completed={500000} workers={500} />);
    expect(container.textContent).toContain("Job Queue");
}); });
