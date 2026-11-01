import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSealedSecPanel } from "@/components/fleet-sealed-sec-panel";
describe("FleetSealedSecPanel", () => { it("renders", () => {
    const { container } = render(<FleetSealedSecPanel total={50} sealed={48} unsealed={2} expiredKeys={0} secure={false} />);
    expect(container.textContent).toContain("Sealed Secrets");
    expect(container.textContent).toContain("2 unsealed");
}); });
