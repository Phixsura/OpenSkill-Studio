import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIdempKeyPanel } from "@/components/fleet-ai-idemp-key-panel";
describe("FleetAiIdempKeyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiIdempKeyPanel managers={3} active={3} keys={5000000} prevented={200000} ttl={7200} />);
    expect(container.textContent).toContain("Idempotency");
}); });
