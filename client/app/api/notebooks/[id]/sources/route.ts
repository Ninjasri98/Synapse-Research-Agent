import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Verify the notebook exists and belongs to the user
    const notebook = await prisma.notebook.findUnique({
      where: {
        id,
        userId: session.user.id,
      },
    });

    if (!notebook) {
      return NextResponse.json(
        { error: "Notebook not found" },
        { status: 404 }
      );
    }

    const { sources } = await req.json();

    if (!sources || !Array.isArray(sources)) {
      return NextResponse.json(
        { error: "Invalid sources data" },
        { status: 400 }
      );
    }

    // Process the sources in a transaction
    const result = await prisma.$transaction(async (tx) => {
      // First delete all existing sources
      await tx.notebookSource.deleteMany({
        where: {
          notebookId: id,
        },
      });

      // Create the new sources
      const createdSources = await Promise.all(
        sources.map((source) =>
          tx.notebookSource.create({
            data: {
              notebookId: id,
              sourceType: source.sourceType,
              sourceUrl: source.sourceUrl || null,
              content: source.content || null,
            },
          })
        )
      );

      // Update notebook status to IN_QUEUE and update the notebook's updatedAt
      await Promise.all([
        tx.notebookProcessingStatus.update({
          where: {
            notebookId: id,
          },
          data: {
            status: "IN_QUEUE",
            message: "Notebook updated and queued for processing",
          },
        }),
        tx.notebook.update({
          where: {
            id,
          },
          data: {
            updatedAt: new Date(),
          },
        }),
      ]);

      return { sources: createdSources };
    });

    return NextResponse.json(result);
  } catch (error) {
    console.error("Error updating notebook sources:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}