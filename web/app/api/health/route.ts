import { proxyToBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function GET() {
  return proxyToBackend("/api/v1/health", { method: "GET" });
}
