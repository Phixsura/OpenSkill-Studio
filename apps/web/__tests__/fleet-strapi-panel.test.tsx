import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStrapiPanel } from "@/components/fleet-strapi-panel";
describe("FleetStrapiPanel", () => { it("renders", () => {
    const { container } = render(<FleetStrapiPanel instances={5} running={5} contentTypes={40} entries={200000} />);
    expect(container.textContent).toContain("Strapi");
    expect(container.textContent).toContain("200,000");
}); });
