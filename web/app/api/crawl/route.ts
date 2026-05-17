import { proxyToBackend } from "@/lib/backend";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  const body = (await request.json()) as {
    sourcePath?: string;
    maxArticles?: number;
    persistRaw?: boolean;
    autoIngest?: boolean;
  };

  return proxyToBackend("/api/v1/sources/crawl", {
    method: "POST",
    body: JSON.stringify({
      source_path: body.sourcePath,
      max_articles: body.maxArticles ?? 6,
      persist_raw: body.persistRaw ?? true,
      auto_ingest: body.autoIngest ?? true,
    }),
  });
}
