import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiWtSharePanel } from "@/components/fleet-ai-wt-share-panel";
describe("FleetAiWtSharePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiWtSharePanel configs={3} active={3} sharedLayers={96} savedGb={500} models={20} />);
    expect(container.textContent).toContain("Weight Sharing");
}); });
