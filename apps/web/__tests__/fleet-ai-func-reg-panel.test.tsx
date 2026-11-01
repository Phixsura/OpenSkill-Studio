import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFuncRegPanel } from "@/components/fleet-ai-func-reg-panel";
describe("FleetAiFuncRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFuncRegPanel registries={3} active={3} functions={1000} calls={20000000} latency={20} />);
    expect(container.textContent).toContain("Function Registry");
}); });
