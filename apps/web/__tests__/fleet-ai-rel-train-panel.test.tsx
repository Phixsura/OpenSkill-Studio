import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRelTrainPanel } from "@/components/fleet-ai-rel-train-panel";
describe("FleetAiRelTrainPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRelTrainPanel trains={3} active={3} services={100} releases={20} onTime={98} />);
    expect(container.textContent).toContain("Release Train");
}); });
