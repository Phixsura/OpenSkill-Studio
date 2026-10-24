import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAutogenPanel } from "@/components/fleet-autogen-panel";
describe("FleetAutogenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAutogenPanel groups={5} active={5} conversations={50000} agents={50} />);
    expect(container.textContent).toContain("AutoGen");
}); });
