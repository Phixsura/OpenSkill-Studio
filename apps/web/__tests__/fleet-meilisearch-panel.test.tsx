import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeilisearchPanel } from "@/components/fleet-meilisearch-panel";
describe("FleetMeilisearchPanel", () => { it("renders", () => {
    const { container } = render(<FleetMeilisearchPanel instances={3} healthy={3} indexes={30} documents={15000000} searchP50={8} />);
    expect(container.textContent).toContain("Meilisearch");
}); });
