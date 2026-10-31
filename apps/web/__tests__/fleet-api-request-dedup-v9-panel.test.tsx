import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiRequestDedupV9Panel } from "@/components/fleet-api-request-dedup-v9-panel";
describe("FleetApiRequestDedupV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiRequestDedupV9Panel endpoints={50} duplicates={100} />);
    expect(container.textContent).toContain("Request Dedup v9");
}); });
