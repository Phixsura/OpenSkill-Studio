import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiVersioningV9Panel } from "@/components/fleet-api-versioning-v9-panel";
describe("FleetApiVersioningV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiVersioningV9Panel total={20} deprecated={3} />);
    expect(container.textContent).toContain("API Versioning v9");
}); });
