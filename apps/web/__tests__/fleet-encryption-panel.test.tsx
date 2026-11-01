import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEncryptionPanel } from "@/components/fleet-encryption-panel";
describe("FleetEncryptionPanel", () => { it("renders", () => {
    const { container } = render(<FleetEncryptionPanel total={10} both={8} fullyEncrypted={false} />);
    expect(container.textContent).toContain("Encryption");
    expect(container.textContent).toContain("8/10");
}); });
