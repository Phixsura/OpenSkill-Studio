import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDriftDetPanel } from "@/components/fleet-ai-drift-det-panel";
describe("FleetAiDriftDetPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDriftDetPanel detectors={6} active={6} alerts={3} driftScore={0.03} retrained={2} />);
    expect(container.textContent).toContain("Drift Detection");
}); });
