import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDbReplPanel } from "@/components/fleet-db-repl-panel";
describe("FleetDbReplPanel", () => { it("renders", () => {
    const { container } = render(<FleetDbReplPanel replicas={3} maxLag={2000} avgLag={717} behind={1} healthy={false} />);
    expect(container.textContent).toContain("DB Replication");
    expect(container.textContent).toContain("1 replicas behind");
}); });
