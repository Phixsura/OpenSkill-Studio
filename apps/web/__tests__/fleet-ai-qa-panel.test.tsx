import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiQaPanel } from "@/components/fleet-ai-qa-panel";
describe("FleetAiQaPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiQaPanel systems={4} active={4} questions={20000000} accuracy={96} sources={50000000} />);
    expect(container.textContent).toContain("Question Answerer");
}); });
