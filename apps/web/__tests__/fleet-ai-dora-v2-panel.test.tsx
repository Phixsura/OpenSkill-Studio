import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDoraV2Panel } from "@/components/fleet-ai-dora-v2-panel";
describe("FleetAiDoraV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDoraV2Panel deployFreq={100} leadTime={5} failPct={0.5} mttr={10} classification="Elite" />);
    expect(container.textContent).toContain("DORA Metrics v2");
    expect(container.textContent).toContain("Elite");
}); });
