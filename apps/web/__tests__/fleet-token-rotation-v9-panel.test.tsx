import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTokenRotationV9Panel } from "@/components/fleet-token-rotation-v9-panel";
describe("FleetTokenRotationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTokenRotationV9Panel total={500} expired={0} />);
    expect(container.textContent).toContain("Token Rotation v9");
}); });
