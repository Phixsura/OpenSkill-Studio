import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRollbackPanel } from "@/components/fleet-rollback-panel";
describe("FleetRollbackPanel", () => { it("renders", () => {
    const { container } = render(<FleetRollbackPanel total={3} auto={2} manual={1} />);
    expect(container.textContent).toContain("Rollbacks");
    expect(container.textContent).toContain("2 auto");
}); });
