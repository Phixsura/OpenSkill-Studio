import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiConsistPanel } from "@/components/fleet-api-consist-panel";
describe("FleetApiConsistPanel", () => { it("renders", () => {
    const { container } = render(<FleetApiConsistPanel total={50} consistent={45} inconsistent={5} score={90} />);
    expect(container.textContent).toContain("API Consistency");
    expect(container.textContent).toContain("5 inconsistent");
}); });
