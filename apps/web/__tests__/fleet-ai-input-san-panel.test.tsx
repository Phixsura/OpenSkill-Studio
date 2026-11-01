import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInputSanPanel } from "@/components/fleet-ai-input-san-panel";
describe("FleetAiInputSanPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiInputSanPanel sanitizers={5} active={5} sanitized={200000000} threats={5000} rules={200} />);
    expect(container.textContent).toContain("Input Sanitizer");
}); });
