import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConnectionPoolV9Panel } from "@/components/fleet-connection-pool-v9-panel";
describe("FleetConnectionPoolV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetConnectionPoolV9Panel pools={5} active={30} />);
    expect(container.textContent).toContain("Connection Pool v9");
}); });
