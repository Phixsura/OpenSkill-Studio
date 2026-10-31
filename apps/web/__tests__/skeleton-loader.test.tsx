import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SkeletonLoader } from "@/components/skeleton-loader";

describe("SkeletonLoader", () => {
  it("renders skeletons", () => {
    const { container } = render(
      <SkeletonLoader blocks={[
        { type: "header", w: "60%", h: "32px" },
        { type: "table", rows: 3, cols: 2 },
      ]} />
    );
    const divs = container.querySelectorAll("div");
    expect(divs.length).toBeGreaterThan(5); // header + table rows
  });
});
