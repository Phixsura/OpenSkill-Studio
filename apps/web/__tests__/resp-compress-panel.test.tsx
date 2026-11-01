import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespCompressPanel } from "@/components/resp-compress-panel";
describe("RespCompressPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RespCompressPanel compressionRate={80} compressed={8000} totalRequests={10000} savedMb={50} />
    );
    expect(container.textContent).toContain("Response Compression");
    expect(container.textContent).toContain("80% compressed");
    expect(container.textContent).toContain("50MB saved");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("10,000");
  });
});
