import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLoadShedPanel } from "@/components/fleet-load-shed-panel";
describe("FleetLoadShedPanel", () => { it("renders", () => {
    const { container } = render(<FleetLoadShedPanel total={20} shedding={2} requestsShed={1000} calm={false} />);
    expect(container.textContent).toContain("Load Shedding");
    expect(container.textContent).toContain("2 services shedding");
}); });
