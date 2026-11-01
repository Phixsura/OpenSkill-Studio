import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone295kApp } from "@/components/milestone-295k-app";
describe("Milestone295kApp", () => { it("renders", () => {
    const { container } = render(<Milestone295kApp />);
    expect(container.textContent).toContain("295K");
}); });
