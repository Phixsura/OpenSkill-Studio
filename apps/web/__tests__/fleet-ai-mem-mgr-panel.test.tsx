import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMemMgrPanel } from "@/components/fleet-ai-mem-mgr-panel";
describe("FleetAiMemMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMemMgrPanel managers={5} active={5} totalGb={50000} usedGb={37500} utilization={75} oom={0} />);
    expect(container.textContent).toContain("Memory Manager");
}); });
