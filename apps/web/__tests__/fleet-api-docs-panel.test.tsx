import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDocsPanel } from "@/components/fleet-api-docs-panel";
describe("FleetApiDocsPanel", () => { it("renders", () => {
    const { container } = render(<FleetApiDocsPanel total={30} documented={25} withExamples={20} coveragePct={83.3} />);
    expect(container.textContent).toContain("API Docs");
    expect(container.textContent).toContain("83.3%");
}); });
