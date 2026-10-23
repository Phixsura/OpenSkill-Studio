import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CdnConfigPanel } from "@/components/cdn-config-panel";

describe("CdnConfigPanel", () => {
  const regions = [{ id: "us-east", name: "US East" }, { id: "eu-west", name: "Europe" }];
  it("renders", () => {
    const { container } = render(
      <CdnConfigPanel regions={regions} cacheHitRate={94.5} bandwidthGb={128.5} avgLatencyMs={22} onPurge={vi.fn()} />
    );
    expect(container.textContent).toContain("CDN Configuration");
    expect(container.textContent).toContain("94.5%");
    expect(container.textContent).toContain("128.5 GB");
    expect(container.textContent).toContain("US East");
  });
  it("purge", () => {
    const fn = vi.fn();
    const { container } = render(
      <CdnConfigPanel regions={regions} cacheHitRate={94} bandwidthGb={100} avgLatencyMs={20} onPurge={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Purge Cache")!);
    expect(fn).toHaveBeenCalled();
  });
});
