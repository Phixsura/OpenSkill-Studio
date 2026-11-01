import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAbTestV9Panel } from "@/components/fleet-ab-test-v9-panel";
describe("FleetAbTestV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAbTestV9Panel total={20} running={5} />);
    expect(container.textContent).toContain("A/B Test v9");
}); });
