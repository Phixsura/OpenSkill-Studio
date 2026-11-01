import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiHealthPanel } from "@/components/fleet-api-health-panel";
describe("FleetApiHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetApiHealthPanel score={93} grade="A" />);
    expect(container.textContent).toContain("API Health");
    expect(container.textContent).toContain("93 — A");
}); });
