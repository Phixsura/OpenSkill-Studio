import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRateCountPanel } from "@/components/fleet-ai-rate-count-panel";
describe("FleetAiRateCountPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRateCountPanel counters={5} active={5} rps={2000000} peakRps={5000000} windows={20} />);
    expect(container.textContent).toContain("Rate Counter");
}); });
