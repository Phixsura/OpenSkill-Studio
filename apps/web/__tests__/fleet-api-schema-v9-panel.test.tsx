import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSchemaV9Panel } from "@/components/fleet-api-schema-v9-panel";
describe("FleetApiSchemaV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSchemaV9Panel schemas={50} versions={200} />);
    expect(container.textContent).toContain("API Schema v9");
}); });
