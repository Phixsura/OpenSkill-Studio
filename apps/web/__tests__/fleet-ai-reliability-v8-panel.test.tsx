import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReliabilityV8Panel } from "@/components/fleet-ai-reliability-v8-panel";
describe("FleetAiReliabilityV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiReliabilityV8Panel systems={5} active={5} uptime={99.9999} mttr={2} budget={85} />);
    expect(container.textContent).toContain("Reliability v8");
}); });
