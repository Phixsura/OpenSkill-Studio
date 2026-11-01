import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDatabaseHealthV9Panel } from "@/components/fleet-database-health-v9-panel";
describe("FleetDatabaseHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDatabaseHealthV9Panel databases={5} qps={50000} />);
    expect(container.textContent).toContain("Database Health v9");
}); });
