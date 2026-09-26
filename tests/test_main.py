import main as main_module


def test_main(monkeypatch):
    calls = []

    class FakeMapping:
        img = "image"
        history = [(0, "contender")]

        def tournament(self):
            calls.append("tournament")

    class FakeViewer:
        def __init__(self, img, history):
            calls.append(("viewer", img, history))

        def show(self):
            calls.append("show")

    monkeypatch.setattr(main_module, "Mapping", FakeMapping)
    monkeypatch.setattr(main_module, "Viewer", FakeViewer)
    main_module.main()

    # The evolution runs first, then its history is handed to the viewer.
    assert calls == [
        "tournament",
        ("viewer", "image", [(0, "contender")]),
        "show",
    ]
