import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataAugPanel } from "@/components/fleet-ai-data-aug-panel";
describe("FleetAiDataAugPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataAugPanel pipelines={6} active={6} samples={200000000} multiplier={15} techniques={12} />);
    expect(container.textContent).toContain("Data Augmentation");
}); });
