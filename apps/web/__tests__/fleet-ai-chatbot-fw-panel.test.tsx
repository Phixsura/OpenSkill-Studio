import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChatbotFwPanel } from "@/components/fleet-ai-chatbot-fw-panel";
describe("FleetAiChatbotFwPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChatbotFwPanel bots={10} active={10} conversations={2000000} csat={4.7} containment={85} />);
    expect(container.textContent).toContain("Chatbot Framework");
}); });
