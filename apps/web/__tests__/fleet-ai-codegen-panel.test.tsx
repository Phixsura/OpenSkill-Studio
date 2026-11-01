import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCodegenPanel } from "@/components/fleet-ai-codegen-panel";
describe("FleetAiCodegenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCodegenPanel engines={4} active={4} completions={20000000} acceptanceRate={45} languages={15} />);
    expect(container.textContent).toContain("Code Generation");
}); });
