import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPrismicPanel } from "@/components/fleet-prismic-panel";
describe("FleetPrismicPanel", () => { it("renders", () => {
    const { container } = render(<FleetPrismicPanel repos={5} active={5} documents={50000} slices={500} />);
    expect(container.textContent).toContain("Prismic");
}); });
