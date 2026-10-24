import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone295kFinal } from "@/components/milestone-295k-final";
describe("Milestone295kFinal", () => { it("renders", () => {
    const { container } = render(<Milestone295kFinal />);
    expect(container.textContent).toContain("295K+");
    expect(container.textContent).toContain("COUNTDOWN");
}); });
