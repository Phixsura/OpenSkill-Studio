import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSchemaRegPanel } from "@/components/fleet-ai-schema-reg-panel";
describe("FleetAiSchemaRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSchemaRegPanel registries={2} active={2} schemas={500} versions={3000} validations={200000000} />);
    expect(container.textContent).toContain("Schema Registry");
}); });
