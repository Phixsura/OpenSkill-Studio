import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataPipePanel } from "@/components/fleet-ai-data-pipe-panel";
describe("FleetAiDataPipePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataPipePanel pipelines={10} active={10} records={200000000} qualityScore={95} />);
    expect(container.textContent).toContain("AI Data Pipeline");
}); });
