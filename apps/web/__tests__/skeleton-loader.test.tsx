import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SkeletonLoader } from "@/components/skeleton-loader";

describe("SkeletonLoader", () => {
  it("renders skeletons", () => {
    const { container } = render(<SkeletonLoader count={5} />);
    expect(container.querySelectorAll("[class*='animate-pulse']").length).toBe(5);
  });
  it("default count", () => {
    const { container } = render(<SkeletonLoader />);
    expect(container.querySelectorAll("[class*='animate-pulse']").length).toBe(3);
  });
});
