import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPenTestV9Panel } from "@/components/fleet-pen-test-v9-panel";
describe("FleetPenTestV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPenTestV9Panel total={20} open={0} />);
    expect(container.textContent).toContain("Pen Test v9");
}); });
