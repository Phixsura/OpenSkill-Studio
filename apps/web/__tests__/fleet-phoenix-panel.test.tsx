import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPhoenixPanel } from "@/components/fleet-phoenix-panel";
describe("FleetPhoenixPanel", () => { it("renders", () => {
    const { container } = render(<FleetPhoenixPanel apps={5} running={5} channels={100} wsConnections={50000} />);
    expect(container.textContent).toContain("Phoenix");
    expect(container.textContent).toContain("50,000 WS");
}); });
