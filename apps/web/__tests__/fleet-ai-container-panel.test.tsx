import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiContainerPanel } from "@/components/fleet-ai-container-panel";
describe("FleetAiContainerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiContainerPanel runtimes={5} active={5} containers={1000} images={200} startup={2} />);
    expect(container.textContent).toContain("AI Containers");
}); });
