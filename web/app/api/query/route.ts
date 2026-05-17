import { proxyToBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json()) as { question?: string; topK?: number };

  return proxyToBackend("/api/v1/knowledge/query", {
    method: "POST",
    body: JSON.stringify({
      question: body.question ?? "",
      top_k: body.topK ?? 4,
    }),
  });
}
