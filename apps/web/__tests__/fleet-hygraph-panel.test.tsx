import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHygraphPanel } from "@/components/fleet-hygraph-panel";
describe("FleetHygraphPanel", () => { it("renders", () => {
    const { container } = render(<FleetHygraphPanel projects={5} active={5} models={50} entries={200000} />);
    expect(container.textContent).toContain("Hygraph");
}); });
