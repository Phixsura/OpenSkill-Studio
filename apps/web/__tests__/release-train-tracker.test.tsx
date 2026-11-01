import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseTrainTracker } from "@/components/release-train-tracker";

describe("ReleaseTrainTracker", () => {
  it("renders train", () => {
    const onApprove = vi.fn();
    const { container, getByText } = render(
      <ReleaseTrainTracker version="3.5.0" status="planning" approved={1} total={2}
        onApprove={onApprove} onRelease={vi.fn()}
        items={[
          { service: "api", version: "3.5.0", status: "approved", testsPassed: true },
          { service: "web", version: "3.5.0", status: "pending", testsPassed: false },
        ]} />
    );
    expect(container.textContent).toContain("Release Train");
    expect(container.textContent).toContain("v3.5.0");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("api");
    fireEvent.click(getByText("Approve"));
    expect(onApprove).toHaveBeenCalledWith("web");
  });
});
