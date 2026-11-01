import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiTestingV9Panel } from "@/components/fleet-api-testing-v9-panel";
describe("FleetApiTestingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiTestingV9Panel suites={20} passed={2000} />);
    expect(container.textContent).toContain("API Testing v9");
}); });
