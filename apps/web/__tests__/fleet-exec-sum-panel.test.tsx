import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetExecSumPanel } from "@/components/fleet-exec-sum-panel";
describe("FleetExecSumPanel", () => { it("renders", () => {
    const { container } = render(<FleetExecSumPanel uptimePct={99.995} deployFreq={15} mttrMin={30} cfrPct={3} doraGrade="Elite" />);
    expect(container.textContent).toContain("Executive Summary");
    expect(container.textContent).toContain("DORA: Elite");
}); });
