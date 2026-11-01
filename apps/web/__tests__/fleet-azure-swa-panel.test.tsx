import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAzureSwaPanel } from "@/components/fleet-azure-swa-panel";
describe("FleetAzureSwaPanel", () => { it("renders", () => {
    const { container } = render(<FleetAzureSwaPanel apps={5} deployed={5} apiFunctions={20} customDomains={10} />);
    expect(container.textContent).toContain("Azure SWA");
}); });
