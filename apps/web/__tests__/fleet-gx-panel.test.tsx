import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGxPanel } from "@/components/fleet-gx-panel";
describe("FleetGxPanel", () => { it("renders", () => {
    const { container } = render(<FleetGxPanel projects={5} active={5} expectations={1000} validations={50000} successRate={99.5} />);
    expect(container.textContent).toContain("Great Expectations");
}); });
