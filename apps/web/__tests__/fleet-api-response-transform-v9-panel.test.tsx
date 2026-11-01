import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiResponseTransformV9Panel } from "@/components/fleet-api-response-transform-v9-panel";
describe("FleetApiResponseTransformV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiResponseTransformV9Panel transforms={30} applied={100000} />);
    expect(container.textContent).toContain("Response Transform v9");
}); });
