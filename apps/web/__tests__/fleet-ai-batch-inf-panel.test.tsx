import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBatchInfPanel } from "@/components/fleet-ai-batch-inf-panel";
describe("FleetAiBatchInfPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBatchInfPanel jobs={20} running={5} completed={15} samples={50000000} latency={8} />);
    expect(container.textContent).toContain("Batch Inference");
}); });
