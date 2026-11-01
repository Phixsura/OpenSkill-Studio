import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApiDocsPanel } from "@/components/fleet-ai-api-docs-panel";
describe("FleetAiApiDocsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiApiDocsPanel generators={3} active={3} endpoints={1000} examples={5000} views={500000} />);
    expect(container.textContent).toContain("API Docs");
}); });
