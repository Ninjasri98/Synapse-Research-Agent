import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { headers } from "next/headers";

export async function GET() {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const notebooks = await prisma.notebook.findMany({
      where: {
        userId: session.user.id,
      },
      orderBy: {
        createdAt: "desc",
      },
      include: {
        processingStatus: true,
      },
    });

    return NextResponse.json(notebooks);
  } catch (error) {
    console.error("Error fetching notebooks:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const { topic, sources } = await request.json();

    const notebookCount = await prisma.notebook.count({
      where: {
        userId: session.user.id,
      },
    });

    const result = await prisma.$transaction(async (tx) => {
      const notebook = await tx.notebook.create({
        data: {
          userId: session.user.id,
          title: `New Notebook ${notebookCount + 1}`,
          topic: topic || null,
        },
      });

      // Create sources if provided
      if (sources && Array.isArray(sources) && sources.length > 0) {
        await Promise.all(
          sources.map((source) =>
            tx.notebookSource.create({
              data: {
                notebookId: notebook.id,
                sourceType: source.sourceType,
                sourceUrl: source.sourceUrl || null,
                content: source.content || null,
                filePath: source.filePath || null,
                filename: source.filename || null,
              },
            })
          )
        );
      }

      const processingStatus = await tx.notebookProcessingStatus.create({
        data: {
          notebookId: notebook.id,
          status: "IN_QUEUE",
          message: "Notebook created and queued for processing",
        },
      });

      return { notebook, processingStatus };
    });

    // Call the research API
    if (result.notebook && (result.notebook.topic || sources.length > 0)) {
      try {
        const researchApiUrl = process.env.BACKEND_API_URL;

        const sourcesToSend = sources && sources.length > 0 ? sources.map((source: { sourceType: string; sourceUrl: string; content: string; filePath: string; filename: string }) => ({
          source_type: source.sourceType,
          source_url: source.sourceUrl || source.filePath || null,
          source_content: source.content || null,
        }))
          : [];

        const researchApiRequestBody = {
          topic: result.notebook.topic || null,
          sources: sourcesToSend,
          notebook_id: result.notebook.id,
        }

        console.log(researchApiRequestBody);

        const researchApiResponse = await fetch(`${researchApiUrl}/api/research`, {
          method: "POST",
          headers: {
            "content-type": "application/json",
          },
          body: JSON.stringify(researchApiRequestBody),
        });

        if (!researchApiResponse.ok) {
          throw new Error(`Research API call failed with status: ${researchApiResponse.status}`);
        }

      } catch (researchApiError) {
        console.error("Error calling research API or BACKEND_API_URL not set:", researchApiError);

        await prisma.notebook.delete({
          where: { id: result.notebook.id },
        });
        console.log(`Successfully deleted notebook ${result.notebook.id} after research API failure.`);

        return NextResponse.json(
          { error: "Notebook creation failed. Please try again." },
          { status: 500 }
        );
      }
    }

    return NextResponse.json(result.notebook);
  } catch (error) {
    console.error("Error creating notebook:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}