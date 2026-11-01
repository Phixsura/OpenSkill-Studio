import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ConfigSnapshotCard from "../src/components/api-developer-platform-sdk-consumer-api-config-snapshot-card";

describe("ConfigSnapshotCard", () => {
  it("renders title and snapshots", () => {
    const { container } = render(<ConfigSnapshotCard />);
    expect(container.textContent).toContain("Config Snapshots");
    expect(container.textContent).toContain("Production v2.1");
    expect(container.textContent).toContain("Initial setup");
  });

  it("shows count", () => {
    const { container } = render(<ConfigSnapshotCard />);
    expect(container.textContent).toContain("3 snapshots saved");
  });
});
