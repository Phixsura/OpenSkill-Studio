import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMtIsolatePanel } from "@/components/fleet-ai-mt-isolate-panel";
describe("FleetAiMtIsolatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMtIsolatePanel systems={3} active={3} tenants={5000} isolated={5000} breaches={0} />);
    expect(container.textContent).toContain("Multi-Tenant");
}); });
