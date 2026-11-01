import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEntityLnkPanel } from "@/components/fleet-ai-entity-lnk-panel";
describe("FleetAiEntityLnkPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEntityLnkPanel linkers={3} active={3} entities={100000000} linked={90000000} accuracy={92} />);
    expect(container.textContent).toContain("Entity Linker");
}); });
