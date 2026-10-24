import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLoadTestV9Panel } from "@/components/fleet-load-test-v9-panel";
describe("FleetLoadTestV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLoadTestV9Panel tests={20} maxRps={50000} />);
    expect(container.textContent).toContain("Load Test v9");
}); });
