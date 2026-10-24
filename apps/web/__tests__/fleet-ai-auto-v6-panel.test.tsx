import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAutoV6Panel } from "@/components/fleet-ai-auto-v6-panel";
describe("FleetAiAutoV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAutoV6Panel systems={5} active={5} automations={5000} tasks={5000000} toil={98} />);
    expect(container.textContent).toContain("Automation v6");
}); });
