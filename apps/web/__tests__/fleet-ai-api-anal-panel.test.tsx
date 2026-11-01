import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApiAnalPanel } from "@/components/fleet-ai-api-anal-panel";
describe("FleetAiApiAnalPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiApiAnalPanel dashboards={3} active={3} endpoints={200} calls={200000000} errorRate={0.1} />);
    expect(container.textContent).toContain("API Analytics");
}); });
