import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEventSchemaV9Panel } from "@/components/fleet-event-schema-v9-panel";
describe("FleetEventSchemaV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEventSchemaV9Panel schemas={50} compatible={50} />);
    expect(container.textContent).toContain("Event Schema v9");
}); });
