import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTelepresencePanel } from "@/components/fleet-telepresence-panel";
describe("FleetTelepresencePanel", () => { it("renders", () => {
    const { container } = render(<FleetTelepresencePanel totalSessions={5} active={2} intercepts={4} />);
    expect(container.textContent).toContain("Telepresence");
    expect(container.textContent).toContain("4 intercepts");
}); });
