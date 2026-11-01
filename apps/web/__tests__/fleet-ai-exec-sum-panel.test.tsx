import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExecSumPanel } from "@/components/fleet-ai-exec-sum-panel";
describe("FleetAiExecSumPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExecSumPanel revenue={500000000} cost={150000000} margin={70} users={5000000} uptime={99.999} />);
    expect(container.textContent).toContain("Executive Summary");
}); });
