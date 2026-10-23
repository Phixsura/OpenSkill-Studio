import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DistLocksPanel } from "@/components/dist-locks-panel";

describe("DistLocksPanel", () => {
  it("renders locks", () => {
    const onRelease = vi.fn();
    const { container, getByText } = render(
      <DistLocksPanel activeLocks={1} onRelease={onRelease}
        locks={[{ key: "deploy", owner: "worker-1" }]} />
    );
    expect(container.textContent).toContain("Distributed Locks");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("deploy");
    expect(container.textContent).toContain("worker-1");
    fireEvent.click(getByText("Force Release"));
    expect(onRelease).toHaveBeenCalledWith("deploy");
  });
});
