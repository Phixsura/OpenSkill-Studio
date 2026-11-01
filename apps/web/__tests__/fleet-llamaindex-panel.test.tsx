import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLlamaindexPanel } from "@/components/fleet-llamaindex-panel";
describe("FleetLlamaindexPanel", () => { it("renders", () => {
    const { container } = render(<FleetLlamaindexPanel apps={5} active={5} indexes={20} queries={1000000} />);
    expect(container.textContent).toContain("LlamaIndex");
}); });
