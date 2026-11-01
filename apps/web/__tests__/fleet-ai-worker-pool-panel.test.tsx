import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWorkerPoolPanel } from "@/components/fleet-ai-worker-pool-panel";
describe("FleetAiWorkerPoolPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWorkerPoolPanel pools={5} active={5} workers={1000} busy={800} idle={200} utilization={80} />);
    expect(container.textContent).toContain("Worker Pool");
}); });
