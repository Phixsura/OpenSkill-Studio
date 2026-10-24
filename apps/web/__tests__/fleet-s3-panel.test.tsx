import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetS3Panel } from "@/components/fleet-s3-panel";
describe("FleetS3Panel", () => { it("renders", () => {
    const { container } = render(<FleetS3Panel buckets={50} objects={5000000} sizeTb={100} encrypted={48} secure={false} />);
    expect(container.textContent).toContain("S3");
    expect(container.textContent).toContain("2 unencrypted");
}); });
