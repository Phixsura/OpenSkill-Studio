import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSecretRotPanel } from "@/components/fleet-ai-secret-rot-panel";
describe("FleetAiSecretRotPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSecretRotPanel rotators={3} active={3} secrets={1000} rotations={100} avgAge={10} />);
    expect(container.textContent).toContain("Secret Rotation");
}); });
