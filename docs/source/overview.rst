Overview
========

Vectorvision is a tool for vectorizing raster graphics, written on the basis of the potrace (https://potrace.sourceforge.net/) program. A detailed description of the algorithm can be found in the publication about potrace (https://potrace.sourceforge.net/potrace.pdf).
For now, available color formats are binary and grayscale. You can convert images of any common format including: png, jpg, jpeg. The output format is SVG.
The algorithm is divided into 5 main steps. Here is the short overview of them.

**1. Path decomposition:**

Convert the bitmap image into a set of discrete paths that outline the boundaries between black and white regions. This involves scanning the image to identify connected components of black pixels. Each connected component is traced to form a path, which captures the structure of the image.

**2. Polygons creation:**

Approximate the decomposed paths with a series of straight-line segments, forming polygons. The paths identified in the previous step are broken down into a sequence of vertices connected by straight lines. This step simplifies the complex curves of the original paths into simpler geometric shapes.

**3. Vertex adjustment:**

Refine the vertices of the polygons to enhance accuracy and better capture the contours of the original image. Vertices are adjusted by optimizing their positions to reduce the deviation from the actual image edges. This may involve techniques such as moving vertices to better align with the image boundaries or averaging positions to smooth out noise.

**4. Smoothing and corner analysis:**

Apply smoothing algorithms to the polygon paths and analyze corners to maintain sharp features where necessary. Smoothing algorithms, such as averaging or spline fitting, are applied to create more fluid and visually appealing lines. Corners are specifically analyzed to decide if they should be kept sharp or smoothed, preserving important details of the image.

**5. Curve optimization:**

Replace the polygonal paths with Bezier curves to create smooth, continuous lines. The straight-line segments of the polygons are replaced with Bezier curves, which provide a more accurate and aesthetically pleasing representation of the image. These curves are optimized to minimize the difference between the vector representation and the original bitmap, ensuring a high-quality vector graphic.
