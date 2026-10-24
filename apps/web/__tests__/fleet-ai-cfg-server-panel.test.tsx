import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCfgServerPanel } from "@/components/fleet-ai-cfg-server-panel";
describe("FleetAiCfgServerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCfgServerPanel servers={3} active={3} configs={2000} clients={1000} updates={500} />);
    expect(container.textContent).toContain("Config Server");
}); });
