import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RuntimeProfiler } from "@/components/runtime-profiler";

describe("RuntimeProfiler", () => {
  it("renders", () => {
    const { container } = render(
      <RuntimeProfiler gcPauseMs={5} heapPct={50} eventLoopLagMs={2}
        activeHandles={50} health="healthy" issues={[]} />
    );
    expect(container.textContent).toContain("Runtime Profiler");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("5ms");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("2ms");
    expect(container.textContent).toContain("50");
  });
});
