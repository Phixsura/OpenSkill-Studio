import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiRateControlV9Panel } from "@/components/fleet-api-rate-control-v9-panel";
describe("FleetApiRateControlV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiRateControlV9Panel policies={20} throttled={10} />);
    expect(container.textContent).toContain("API Rate Control v9");
}); });
