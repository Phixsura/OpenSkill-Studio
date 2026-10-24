import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiQaPanel } from "@/components/fleet-ai-qa-panel";
describe("FleetAiQaPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiQaPanel services={5} active={5} questions={5000000} accuracy={96} />);
    expect(container.textContent).toContain("AI QA");
}); });
