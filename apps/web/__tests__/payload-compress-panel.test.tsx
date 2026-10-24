import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PayloadCompressPanel } from "@/components/payload-compress-panel";
describe("PayloadCompressPanel", () => {
  it("renders", () => {
    const { container } = render(
      <PayloadCompressPanel originalBytes={10240} compressedBytes={3072} ratioPct={70} totalCompressed={5000} />
    );
    expect(container.textContent).toContain("Payload Compression");
    expect(container.textContent).toContain("70% saved");
    expect(container.textContent).toContain("5000 compressed");
    expect(container.textContent).toContain("10.0KB");
    expect(container.textContent).toContain("3.0KB");
  });
});
