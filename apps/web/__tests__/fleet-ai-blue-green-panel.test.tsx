import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBlueGreenPanel } from "@/components/fleet-ai-blue-green-panel";
describe("FleetAiBlueGreenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBlueGreenPanel deploys={6} active={6} switches={20} rollbackS={3} zeroDowntime={true} />);
    expect(container.textContent).toContain("Blue-Green");
}); });
