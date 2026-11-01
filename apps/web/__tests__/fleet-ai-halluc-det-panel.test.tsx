import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHallucDetPanel } from "@/components/fleet-ai-halluc-det-panel";
describe("FleetAiHallucDetPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHallucDetPanel detectors={4} active={4} checked={20000000} hallucinations={15000} detectionRate={97} />);
    expect(container.textContent).toContain("Hallucination Detector");
}); });
