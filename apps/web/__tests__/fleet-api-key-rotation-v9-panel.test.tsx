import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiKeyRotationV9Panel } from "@/components/fleet-api-key-rotation-v9-panel";
describe("FleetApiKeyRotationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiKeyRotationV9Panel keys={500} expired={0} />);
    expect(container.textContent).toContain("API Key Rotation v9");
}); });
