import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOutboxPanel } from "@/components/fleet-ai-outbox-panel";
describe("FleetAiOutboxPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOutboxPanel processors={4} active={4} messages={200000000} pending={5} published={199999995} />);
    expect(container.textContent).toContain("Outbox Processor");
}); });
