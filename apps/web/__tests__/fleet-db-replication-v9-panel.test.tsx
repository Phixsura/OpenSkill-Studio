import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDbReplicationV9Panel } from "@/components/fleet-db-replication-v9-panel";
describe("FleetDbReplicationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDbReplicationV9Panel replicas={5} maxLag={10} />);
    expect(container.textContent).toContain("DB Replication v9");
}); });
