import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiTransformV9Panel } from "@/components/fleet-api-transform-v9-panel";
describe("FleetApiTransformV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiTransformV9Panel transforms={30} active={28} />);
    expect(container.textContent).toContain("API Transform v9");
}); });
