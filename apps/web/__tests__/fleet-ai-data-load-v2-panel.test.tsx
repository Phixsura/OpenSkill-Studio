import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataLoadV2Panel } from "@/components/fleet-ai-data-load-v2-panel";
describe("FleetAiDataLoadV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataLoadV2Panel loaders={5} active={5} throughput={500} prefetch={32} workers={128} />);
    expect(container.textContent).toContain("Data Loader v2");
}); });
