import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBiasDetPanel } from "@/components/fleet-ai-bias-det-panel";
describe("FleetAiBiasDetPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBiasDetPanel detectors={4} active={4} scans={200000} alerts={5} fairness={0.96} />);
    expect(container.textContent).toContain("Bias Detection");
}); });
