import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourceUsageBars } from "@/components/resource-usage-bars";

describe("ResourceUsageBars", () => {
  it("renders all bars", () => {
    const { container } = render(
      <ResourceUsageBars cpuPct={50} memoryMb={128} memoryLimitMb={256} networkKb={5000} networkLimitKb={10240} />
    );
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("Memory");
    expect(container.textContent).toContain("Network");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("128MB");
  });
});
