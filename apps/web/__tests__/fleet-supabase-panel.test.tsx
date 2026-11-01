import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSupabasePanel } from "@/components/fleet-supabase-panel";
describe("FleetSupabasePanel", () => { it("renders", () => {
    const { container } = render(<FleetSupabasePanel projects={10} active={10} dbSize={200} apiRequests={5000000} />);
    expect(container.textContent).toContain("Supabase");
    expect(container.textContent).toContain("5,000,000");
}); });
