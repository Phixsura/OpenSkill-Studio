import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataLinPanel } from "@/components/fleet-ai-data-lin-panel";
describe("FleetAiDataLinPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataLinPanel trackers={4} active={4} datasets={1000} transforms={10000} depth={20} />);
    expect(container.textContent).toContain("Data Lineage");
}); });
