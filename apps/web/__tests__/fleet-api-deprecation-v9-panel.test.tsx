import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDeprecationV9Panel } from "@/components/fleet-api-deprecation-v9-panel";
describe("FleetApiDeprecationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDeprecationV9Panel total={100} deprecated={5} />);
    expect(container.textContent).toContain("API Deprecation v9");
}); });
