import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGlobalLbV9Panel } from "@/components/fleet-global-lb-v9-panel";
describe("FleetGlobalLbV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGlobalLbV9Panel regions={10} rps={500000} />);
    expect(container.textContent).toContain("Global LB v9");
}); });
