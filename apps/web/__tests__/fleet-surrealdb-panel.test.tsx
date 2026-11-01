import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSurrealdbPanel } from "@/components/fleet-surrealdb-panel";
describe("FleetSurrealdbPanel", () => { it("renders", () => {
    const { container } = render(<FleetSurrealdbPanel instances={3} running={3} namespaces={10} tables={200} />);
    expect(container.textContent).toContain("SurrealDB");
}); });
