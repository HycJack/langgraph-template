from IPython.display import Image, display
from agent import build_graph
try:
    graph = build_graph()
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

try:
    graph = build_graph()
    png_data = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(png_data)
    display(Image(png_data))
except Exception as e:
    print(f"Error generating or saving graph: {e}")
    # This requires some extra dependencies and is optional
    pass
