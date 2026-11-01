import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSchemaRegistryV9Panel } from "@/components/fleet-schema-registry-v9-panel";
describe("FleetSchemaRegistryV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSchemaRegistryV9Panel schemas={100} versions={500} />);
    expect(container.textContent).toContain("Schema Registry v9");
}); });
