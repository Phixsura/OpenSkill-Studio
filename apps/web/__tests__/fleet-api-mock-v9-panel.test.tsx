import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiMockV9Panel } from "@/components/fleet-api-mock-v9-panel";
describe("FleetApiMockV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiMockV9Panel mocks={10} requests={50000} />);
    expect(container.textContent).toContain("API Mock v9");
}); });
