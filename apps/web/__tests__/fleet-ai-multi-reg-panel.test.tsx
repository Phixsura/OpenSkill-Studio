import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMultiRegPanel } from "@/components/fleet-ai-multi-reg-panel";
describe("FleetAiMultiRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMultiRegPanel deployments={5} active={5} regions={8} rps={2000000} failoverOk={true} />);
    expect(container.textContent).toContain("Multi-Region");
}); });
