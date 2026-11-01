import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSnowflakePanel } from "@/components/fleet-snowflake-panel";
describe("FleetSnowflakePanel", () => { it("renders", () => {
    const { container } = render(<FleetSnowflakePanel warehouses={5} running={3} credits={75} queries={50000} />);
    expect(container.textContent).toContain("Snowflake");
    expect(container.textContent).toContain("50,000");
}); });
