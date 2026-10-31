import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFeedbackV7Panel } from "@/components/fleet-ai-feedback-v7-panel";
describe("FleetAiFeedbackV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiFeedbackV7Panel systems={3} active={3} feedback={500000} positive={450000} actioned={20000} />);
    expect(container.textContent).toContain("Feedback v7");
}); });
