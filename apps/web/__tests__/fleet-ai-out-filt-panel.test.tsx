import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOutFiltPanel } from "@/components/fleet-ai-out-filt-panel";
describe("FleetAiOutFiltPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOutFiltPanel filters={4} active={4} filtered={200000000} blocked={20000} rules={200} />);
    expect(container.textContent).toContain("Output Filter");
}); });
