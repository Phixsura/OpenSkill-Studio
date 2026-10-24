import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataPipeV2Panel } from "@/components/fleet-ai-data-pipe-v2-panel";
describe("FleetAiDataPipeV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataPipeV2Panel pipelines={5} active={5} stages={50} records={2000000000} throughput={10000} />);
    expect(container.textContent).toContain("Data Pipeline v2");
}); });
