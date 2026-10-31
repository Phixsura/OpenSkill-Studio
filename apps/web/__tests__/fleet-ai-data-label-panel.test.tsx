import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataLabelPanel } from "@/components/fleet-ai-data-label-panel";
describe("FleetAiDataLabelPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataLabelPanel projects={6} active={6} labeled={500000} pending={20000} accuracy={98} />);
    expect(container.textContent).toContain("Data Labeling");
}); });
