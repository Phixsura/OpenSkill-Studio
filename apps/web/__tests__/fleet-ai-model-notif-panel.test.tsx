import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelNotifPanel } from "@/components/fleet-ai-model-notif-panel";
describe("FleetAiModelNotifPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelNotifPanel systems={3} active={3} notifications={200000} channels={15} subscribers={20000} />);
    expect(container.textContent).toContain("Model Notifications");
}); });
