import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPostgresPanel } from "@/components/fleet-postgres-panel";
describe("FleetPostgresPanel", () => { it("renders", () => {
    const { container } = render(<FleetPostgresPanel instances={3} primary={1} replicas={2} maxLag={5} activeConns={80} healthy={true} />);
    expect(container.textContent).toContain("PostgreSQL");
    expect(container.textContent).toContain("1P/2R");
}); });
