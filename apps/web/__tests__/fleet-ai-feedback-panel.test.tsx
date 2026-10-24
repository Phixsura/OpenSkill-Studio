import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFeedbackPanel } from "@/components/fleet-ai-feedback-panel";
describe("FleetAiFeedbackPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFeedbackPanel systems={4} active={4} feedback={500000} thumbsUp={450000} thumbsDown={50000} satisfaction={90} />);
    expect(container.textContent).toContain("Feedback Loop");
}); });
