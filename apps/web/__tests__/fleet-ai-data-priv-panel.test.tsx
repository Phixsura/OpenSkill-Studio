import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataPrivPanel } from "@/components/fleet-ai-data-priv-panel";
describe("FleetAiDataPrivPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataPrivPanel systems={3} active={3} epsilon={0.3} datasets={200} queries={5000000} />);
    expect(container.textContent).toContain("Data Privacy");
}); });
