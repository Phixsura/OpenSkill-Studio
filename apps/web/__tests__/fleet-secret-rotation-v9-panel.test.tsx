import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSecretRotationV9Panel } from "@/components/fleet-secret-rotation-v9-panel";
describe("FleetSecretRotationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSecretRotationV9Panel total={500} rate={99.8} />);
    expect(container.textContent).toContain("Secret Rotation v9");
}); });
