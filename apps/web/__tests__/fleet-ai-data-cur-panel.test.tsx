import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataCurPanel } from "@/components/fleet-ai-data-cur-panel";
describe("FleetAiDataCurPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataCurPanel curators={4} active={4} datasets={200} samples={500000000} quality={97} />);
    expect(container.textContent).toContain("Dataset Curator");
}); });
