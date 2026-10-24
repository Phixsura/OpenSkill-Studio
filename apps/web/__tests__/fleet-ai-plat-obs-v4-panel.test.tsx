import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatObsV4Panel } from "@/components/fleet-ai-plat-obs-v4-panel";
describe("FleetAiPlatObsV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatObsV4Panel systems={5} active={5} metrics={5000000000} traces={2000000000} logs={20000000000} cardinality={500000} />);
    expect(container.textContent).toContain("Observability v4");
}); });
