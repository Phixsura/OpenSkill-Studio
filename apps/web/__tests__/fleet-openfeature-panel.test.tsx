import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpenfeaturePanel } from "@/components/fleet-openfeature-panel";
describe("FleetOpenfeaturePanel", () => { it("renders", () => {
    const { container } = render(<FleetOpenfeaturePanel total={3} active={3} evaluations={500000} />);
    expect(container.textContent).toContain("OpenFeature");
    expect(container.textContent).toContain("500,000");
}); });
