import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDirectusPanel } from "@/components/fleet-directus-panel";
describe("FleetDirectusPanel", () => { it("renders", () => {
    const { container } = render(<FleetDirectusPanel instances={3} running={3} collections={60} items={500000} />);
    expect(container.textContent).toContain("Directus");
    expect(container.textContent).toContain("500,000");
}); });
