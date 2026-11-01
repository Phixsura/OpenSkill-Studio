import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiReliabilityV5Panel } from "@/components/fleet-ai-reliability-v5-panel";
describe("FleetAiReliabilityV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiReliabilityV5Panel systems={5} active={5} uptime={99.9999} mttr={3} budget={85} slis={500} />);
    expect(container.textContent).toContain("Reliability v5");
}); });
