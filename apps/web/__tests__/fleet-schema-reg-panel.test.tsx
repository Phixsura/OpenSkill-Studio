import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSchemaRegPanel } from "@/components/fleet-schema-reg-panel";
describe("FleetSchemaRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetSchemaRegPanel total={10} compatible={9} breaking={1} safe={false} />);
    expect(container.textContent).toContain("Schema Registry");
    expect(container.textContent).toContain("1 breaking");
}); });
