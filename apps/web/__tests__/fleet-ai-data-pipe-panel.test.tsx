import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataPipePanel } from "@/components/fleet-ai-data-pipe-panel";
describe("FleetAiDataPipePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataPipePanel pipelines={8} active={8} records={100000000} throughput={1000} />);
    expect(container.textContent).toContain("Data Pipeline");
}); });
