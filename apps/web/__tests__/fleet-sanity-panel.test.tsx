import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSanityPanel } from "@/components/fleet-sanity-panel";
describe("FleetSanityPanel", () => { it("renders", () => {
    const { container } = render(<FleetSanityPanel projects={5} active={5} documents={500000} datasets={10} />);
    expect(container.textContent).toContain("Sanity");
    expect(container.textContent).toContain("500,000 docs");
}); });
