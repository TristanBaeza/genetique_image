from classes.mapping import Mapping
from classes.viewer import Viewer


def main() -> None:
    mapping = Mapping()
    mapping.tournament()
    Viewer(mapping.img, mapping.history).show()


if __name__ == "__main__":
    main()
