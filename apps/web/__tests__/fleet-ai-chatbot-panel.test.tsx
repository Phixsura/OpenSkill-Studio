import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChatbotPanel } from "@/components/fleet-ai-chatbot-panel";
describe("FleetAiChatbotPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChatbotPanel bots={20} active={20} conversations={2000000} satisfaction={92} />);
    expect(container.textContent).toContain("AI Chatbot");
}); });
