import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBatchProcPanel } from "@/components/fleet-ai-batch-proc-panel";
describe("FleetAiBatchProcPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBatchProcPanel processors={6} active={6} jobs={10000} items={200000000} throughput={50000} />);
    expect(container.textContent).toContain("Batch Processor");
}); });
