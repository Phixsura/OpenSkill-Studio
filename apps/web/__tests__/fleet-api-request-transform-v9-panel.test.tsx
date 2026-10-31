import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiRequestTransformV9Panel } from "@/components/fleet-api-request-transform-v9-panel";
describe("FleetApiRequestTransformV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiRequestTransformV9Panel transforms={30} applied={50000} />);
    expect(container.textContent).toContain("Request Transform v9");
}); });
