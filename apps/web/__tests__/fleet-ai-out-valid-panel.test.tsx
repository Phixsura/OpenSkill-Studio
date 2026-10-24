import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOutValidPanel } from "@/components/fleet-ai-out-valid-panel";
describe("FleetAiOutValidPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOutValidPanel validators={4} active={4} validated={20000000} rejected={5000} rules={100} />);
    expect(container.textContent).toContain("Output Validator");
}); });
