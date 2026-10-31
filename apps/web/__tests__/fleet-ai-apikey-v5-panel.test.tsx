import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApikeyV5Panel } from "@/components/fleet-ai-apikey-v5-panel";
describe("FleetAiApikeyV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiApikeyV5Panel managers={3} active={3} keys={500000} created={1000} revoked={200} />);
    expect(container.textContent).toContain("API Key v5");
}); });
