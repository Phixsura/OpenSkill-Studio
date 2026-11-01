import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLearnDbPanel } from "@/components/fleet-learn-db-panel";
describe("FleetLearnDbPanel", () => { it("renders", () => {
    const { container } = render(<FleetLearnDbPanel totalEntries={100} categories={10} rich={true} />);
    expect(container.textContent).toContain("Learnings DB");
    expect(container.textContent).toContain("Rich knowledge");
}); });
