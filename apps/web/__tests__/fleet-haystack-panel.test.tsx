import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHaystackPanel } from "@/components/fleet-haystack-panel";
describe("FleetHaystackPanel", () => { it("renders", () => {
    const { container } = render(<FleetHaystackPanel pipelines={10} active={10} nodes={50} queries={1000000} />);
    expect(container.textContent).toContain("Haystack");
}); });
