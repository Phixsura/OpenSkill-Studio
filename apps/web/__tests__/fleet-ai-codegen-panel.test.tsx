import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCodegenPanel } from "@/components/fleet-ai-codegen-panel";
describe("FleetAiCodegenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCodegenPanel services={5} active={5} completions={5000000} acceptanceRate={38} linesGenerated={2000000} />);
    expect(container.textContent).toContain("AI Code Gen");
}); });
