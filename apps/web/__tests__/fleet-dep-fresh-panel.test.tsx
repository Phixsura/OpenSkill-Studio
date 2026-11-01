import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDepFreshPanel } from "@/components/fleet-dep-fresh-panel";
describe("FleetDepFreshPanel", () => { it("renders", () => {
    const { container } = render(<FleetDepFreshPanel total={50} outdated={10} critical={3} upToDate={false} />);
    expect(container.textContent).toContain("Dependency Freshness");
    expect(container.textContent).toContain("10 outdated");
}); });
