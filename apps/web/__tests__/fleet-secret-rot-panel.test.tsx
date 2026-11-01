import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSecretRotPanel } from "@/components/fleet-secret-rot-panel";
describe("FleetSecretRotPanel", () => { it("renders", () => {
    const { container } = render(<FleetSecretRotPanel total={10} stale={2} compliant={false} />);
    expect(container.textContent).toContain("Secret Rotation");
    expect(container.textContent).toContain("2 stale");
}); });
