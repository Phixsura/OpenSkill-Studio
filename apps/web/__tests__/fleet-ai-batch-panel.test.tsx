import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBatchPanel } from "@/components/fleet-ai-batch-panel";
describe("FleetAiBatchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBatchPanel total={20} completed={15} running={5} itemsProcessed={10000000} />);
    expect(container.textContent).toContain("AI Batch");
}); });
