import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRollUpdPanel } from "@/components/fleet-ai-roll-upd-panel";
describe("FleetAiRollUpdPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRollUpdPanel updaters={5} active={5} updates={60} instances={1000} rollbacks={0} />);
    expect(container.textContent).toContain("Rolling Update");
}); });
