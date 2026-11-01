import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPostgrestPanel } from "@/components/fleet-postgrest-panel";
describe("FleetPostgrestPanel", () => { it("renders", () => {
    const { container } = render(<FleetPostgrestPanel instances={3} running={3} rps={100000} schemas={10} />);
    expect(container.textContent).toContain("PostgREST");
    expect(container.textContent).toContain("100,000");
}); });
