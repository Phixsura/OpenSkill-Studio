import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConvexPanel } from "@/components/fleet-convex-panel";
describe("FleetConvexPanel", () => { it("renders", () => {
    const { container } = render(<FleetConvexPanel projects={5} deployed={5} functions={200} documents={2000000} />);
    expect(container.textContent).toContain("Convex");
}); });
