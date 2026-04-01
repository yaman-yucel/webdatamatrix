import gradio as gr
import zxingcpp
from PIL import Image


def scan_datamatrix(image: Image.Image) -> tuple[str, str]:
    if image is None:
        return "No image provided.", ""

    results = zxingcpp.read_barcodes(image)

    if not results:
        return "No barcode found.", ""

    decoded_texts = []
    metrics_lines = []

    for i, result in enumerate(results, start=1):
        prefix = f"[{i}] " if len(results) > 1 else ""

        decoded_texts.append(f"{prefix}{result.text}")

        fmt = result.format.name if result.format else "Unknown"
        content_type = result.content_type.name if result.content_type else "Unknown"
        position = result.position

        lines = [f"{prefix}Format: {fmt}"]
        lines.append(f"{prefix}Content type: {content_type}")
        lines.append(f"{prefix}Valid: {result.valid}")
        lines.append(f"{prefix}Error: {result.error_message or 'None'}")

        if position:
            corners = [
                f"TL({position.top_left.x},{position.top_left.y})",
                f"TR({position.top_right.x},{position.top_right.y})",
                f"BR({position.bottom_right.x},{position.bottom_right.y})",
                f"BL({position.bottom_left.x},{position.bottom_left.y})",
            ]
            lines.append(f"{prefix}Position: {' | '.join(corners)}")

        if result.orientation is not None:
            lines.append(f"{prefix}Orientation: {result.orientation}°")

        if result.ec_level:
            lines.append(f"{prefix}EC level: {result.ec_level}")

        metrics_lines.extend(lines)
        if len(results) > 1:
            metrics_lines.append("")

    decoded_output = "\n".join(decoded_texts)
    metrics_output = "\n".join(metrics_lines).rstrip()

    return decoded_output, metrics_output


with gr.Blocks(title="Data Matrix Scanner") as demo:
    gr.Markdown("## Data Matrix Barcode Scanner")
    gr.Markdown(
        "Point your camera at a Data Matrix barcode and click **Capture** to scan. "
        "Snap another photo to scan again."
    )

    with gr.Row():
        image_input = gr.Image(
            sources=["webcam", "upload"],
            type="pil",
            label="Camera / Upload",
        )

    with gr.Row():
        decoded_output = gr.Textbox(
            label="Decoded text",
            lines=3,
            interactive=False,
            placeholder="Decoded barcode content will appear here…",
        )

    with gr.Row():
        metrics_output = gr.Textbox(
            label="Scan metrics",
            lines=8,
            interactive=False,
            placeholder="Format, position, orientation and other details will appear here…",
        )

    image_input.change(
        fn=scan_datamatrix,
        inputs=image_input,
        outputs=[decoded_output, metrics_output],
    )

if __name__ == "__main__":
    demo.launch(share=True)
