import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataDedupPanel } from "@/components/fleet-ai-data-dedup-panel";
describe("FleetAiDataDedupPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataDedupPanel dedupers={3} active={3} processed={500000000} removed={75000000} reduction={15} />);
    expect(container.textContent).toContain("Data Dedup");
}); });
