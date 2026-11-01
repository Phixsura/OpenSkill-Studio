import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone300000Lines } from "@/components/milestone-300000-lines";
describe("Milestone300000Lines", () => {
  it("renders the historic 300K milestone", () => {
    const { container } = render(<Milestone300000Lines />);
    expect(container.textContent).toContain("300,000 LINES");
    expect(container.textContent).toContain("Three hundred thousand");
    expect(container.textContent).toContain("DORA ELITE");
    expect(container.textContent).toContain("3,486");
    expect(container.textContent).toContain("13,102");
    expect(container.textContent).toContain("relentless iteration");
  });
});
