import { NextRequest, NextResponse } from "next/server";
import { headers } from "next/headers";
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { auth } from "@/lib/auth";
import {
  r2Client,
  R2_BUCKET_NAME,
  SUPPORTED_FILE_TYPES,
  MAX_FILE_SIZE,
  generateR2FilePath,
  getR2PublicUrl
} from "@/lib/r2";

export async function POST(request: NextRequest) {
  try {
    // Check authentication
    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    // Parse form data
    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json(
        { error: "No file provided" },
        { status: 400 }
      );
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: `File size exceeds maximum limit of ${MAX_FILE_SIZE / (1024 * 1024)}MB` },
        { status: 400 }
      );
    }

    // Validate file type
    if (!Object.keys(SUPPORTED_FILE_TYPES).includes(file.type)) {
      return NextResponse.json(
        { error: `Unsupported file type. Supported types: ${Object.values(SUPPORTED_FILE_TYPES).join(', ')}` },
        { status: 400 }
      );
    }

    // Generate unique file path
    const filePath = generateR2FilePath(session.user.id, file.name);

    // Convert file to buffer
    const fileBuffer = Buffer.from(await file.arrayBuffer());

    // Upload to R2
    const uploadCommand = new PutObjectCommand({
      Bucket: R2_BUCKET_NAME,
      Key: filePath,
      Body: fileBuffer,
      ContentType: file.type,
      ContentLength: file.size,
      Metadata: {
        originalFilename: file.name,
        uploadedBy: session.user.id,
        uploadDate: new Date().toISOString(),
      },
    });

    await r2Client.send(uploadCommand);

    // Generate public URL
    const publicUrl = getR2PublicUrl(filePath);

    return NextResponse.json({
      success: true,
      filePath,
      filename: file.name,
      fileSize: file.size,
      fileType: file.type,
      publicUrl,
    });

  } catch (error) {
    console.error("Error uploading file to R2:", error);
    return NextResponse.json(
      { error: "Failed to upload file" },
      { status: 500 }
    );
  }
}