import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppComparisonTable } from "@/components/app-comparison-table";

describe("AppComparisonTable", () => {
  it("shows app names", () => {
    const { container } = render(<AppComparisonTable appA={{ name: "A" }} appB={{ name: "B" }} differences={{ category: { a: "connector", b: "automation" } }} installA={100} installB={200} />);
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("B");
  });
  it("shows differences", () => {
    const { container } = render(<AppComparisonTable appA={{ name: "A" }} appB={{ name: "B" }} differences={{ category: { a: "connector", b: "automation" } }} installA={0} installB={0} />);
    expect(container.textContent).toContain("connector");
    expect(container.textContent).toContain("automation");
  });
});
