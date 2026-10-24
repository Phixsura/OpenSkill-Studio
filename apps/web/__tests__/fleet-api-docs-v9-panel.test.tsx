import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDocsV9Panel } from "@/components/fleet-api-docs-v9-panel";
describe("FleetApiDocsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDocsV9Panel endpoints={200} coverage={98} />);
    expect(container.textContent).toContain("API Docs v9");
}); });
