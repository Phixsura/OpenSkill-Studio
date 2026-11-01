import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCanaryAnalysisV9Panel } from "@/components/fleet-canary-analysis-v9-panel";
describe("FleetCanaryAnalysisV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCanaryAnalysisV9Panel analyses={20} passed={20} />);
    expect(container.textContent).toContain("Canary Analysis v9");
}); });
