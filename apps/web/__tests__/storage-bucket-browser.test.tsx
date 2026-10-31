import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StorageBucketBrowser } from "@/components/storage-bucket-browser";

describe("StorageBucketBrowser", () => {
  it("renders buckets", () => {
    const { container } = render(
      <StorageBucketBrowser totalObjects={500} totalSizeMb={1200} onCreate={vi.fn()}
        buckets={[
          { name: "assets", region: "us-east-1", objects: 300, sizeMb: 800, public: false },
          { name: "uploads", region: "eu-west-1", objects: 200, sizeMb: 400, public: true },
        ]} />
    );
    expect(container.textContent).toContain("Storage Buckets");
    expect(container.textContent).toContain("500 objects");
    expect(container.textContent).toContain("assets");
    expect(container.textContent).toContain("Private");
    expect(container.textContent).toContain("uploads");
    expect(container.textContent).toContain("Public");
  });
});
