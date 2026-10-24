import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPubsubPanel } from "@/components/fleet-ai-pubsub-panel";
describe("FleetAiPubsubPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPubsubPanel systems={4} active={4} topics={500} subscriptions={2500} messages={2000000000} />);
    expect(container.textContent).toContain("AI PubSub");
}); });
