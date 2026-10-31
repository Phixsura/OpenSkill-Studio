import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSigstorePanel } from "@/components/fleet-sigstore-panel";
describe("FleetSigstorePanel", () => { it("renders", () => {
    const { container } = render(<FleetSigstorePanel total={100} signed={95} verified={95} unsigned={5} secure={false} />);
    expect(container.textContent).toContain("Sigstore");
    expect(container.textContent).toContain("5 unsigned");
}); });
