import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDepGraphPanel } from "@/components/fleet-ai-dep-graph-panel";
describe("FleetAiDepGraphPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDepGraphPanel graphs={2} active={2} services={500} edges={3000} circular={0} />);
    expect(container.textContent).toContain("Dependency Graph");
}); });
