import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRollbackEngineV9Panel } from "@/components/fleet-rollback-engine-v9-panel";
describe("FleetRollbackEngineV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRollbackEngineV9Panel total={10} avgTime={30} />);
    expect(container.textContent).toContain("Rollback Engine v9");
}); });
