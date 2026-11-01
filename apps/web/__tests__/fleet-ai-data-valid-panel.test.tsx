import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataValidPanel } from "@/components/fleet-ai-data-valid-panel";
describe("FleetAiDataValidPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataValidPanel validators={5} active={5} validated={200000000} issues={100000} rules={80} />);
    expect(container.textContent).toContain("Data Validator");
}); });
