import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRemixPanel } from "@/components/fleet-remix-panel";
describe("FleetRemixPanel", () => { it("renders", () => {
    const { container } = render(<FleetRemixPanel apps={5} deployed={5} loaders={100} actions={60} />);
    expect(container.textContent).toContain("Remix");
    expect(container.textContent).toContain("100 loaders");
}); });
